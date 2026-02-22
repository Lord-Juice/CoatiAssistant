from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .canonicalize import canonical_entity, extract_aliases, key_for_entity, normalize_text
from .schemas import EntityRef, HistoryEntry, MemoryObject


class MemoryStore:
    """
    JSON-file backed store.

    Structure on disk:
    {
      "entity:wallet": {MemoryObject...},
      "entity:keys":   {MemoryObject...}
    }
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self._db: Dict[str, Dict[str, Any]] = {}
        self._load()

    # -------------------------
    # Persistence
    # -------------------------
    def _load(self) -> None:
        if not os.path.exists(self.path):
            self._db = {}
            return
        with open(self.path, "r", encoding="utf-8") as f:
            self._db = json.load(f)

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._db, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    # -------------------------
    # Public API
    # -------------------------
    def memory_index(self) -> List[Dict[str, Any]]:
        """
        Returns a structured index to avoid the agent guessing keys.
        """
        out: List[Dict[str, Any]] = []
        for key, obj in self._db.items():
            entity = obj.get("entity", {})
            facts = obj.get("facts", {})
            slots: List[str] = []
            for group_name, group_val in facts.items():
                if isinstance(group_val, dict):
                    for slot_name in group_val.keys():
                        slots.append(f"{group_name}.{slot_name}")
                else:
                    slots.append(group_name)
            out.append(
                {
                    "key": key,
                    "entity": entity.get("canonical"),
                    "aliases": entity.get("aliases", []),
                    "slots": sorted(set(slots)),
                }
            )
        return out

    def upsert_fact(
        self,
        entity_raw: str,
        entity_type: str,
        slot: str,
        value: Any,
        source_utterance: str,
        confidence: float = 1.0,
        source: str = "user",
    ) -> Dict[str, Any]:
        """
        Upsert a single slot like 'location.current'.
        Also keeps history in 'location.history'.
        """
        ent = canonical_entity(entity_raw)
        key = key_for_entity(ent)
        now = datetime.now().astimezone().isoformat()

        obj = self._get_or_create(key=key, canonical=ent, entity_type=entity_type, aliases=extract_aliases(entity_raw))
        obj.touch()
        obj.meta["source_utterance"] = source_utterance

        group, leaf = self._split_slot(slot)
        obj.facts.setdefault(group, {})
        if not isinstance(obj.facts[group], dict):
            # If someone previously stored non-dict here, normalize it.
            obj.facts[group] = {"current": obj.facts[group]}

        # history
        hist_key = "history"
        obj.facts[group].setdefault(hist_key, [])
        if isinstance(obj.facts[group][hist_key], list):
            obj.facts[group][hist_key].append(asdict(HistoryEntry(value=value, at=now, source=source, confidence=confidence)))

        # current
        obj.facts[group][leaf] = value

        self._db[key] = asdict(obj)
        self._save()
        return {"key": key, "slot": slot, "value": value}

    def read_fact(self, entity_raw: str, slot: str) -> Tuple[Optional[Any], Dict[str, Any]]:
        """
        Deterministic retrieval:
        1) canonicalize entity -> direct key
        2) if not found -> alias/fuzzy search in memory_index
        3) if found but slot missing -> return (None, reason)
        """
        ent = canonical_entity(entity_raw)
        key = key_for_entity(ent)

        if key not in self._db:
            key = self._find_best_key(entity_raw)
            if key is None:
                return None, {"status": "not_found", "reason": "entity_not_found"}

        obj = self._db[key]
        group, leaf = self._split_slot(slot)
        facts = obj.get("facts", {})
        group_val = facts.get(group)

        if not isinstance(group_val, dict) or leaf not in group_val:
            return None, {"status": "not_found", "reason": "slot_not_found", "key": key}

        return group_val[leaf], {"status": "ok", "key": key}

    # -------------------------
    # Internals
    # -------------------------
    def _get_or_create(self, key: str, canonical: str, entity_type: str, aliases: List[str]) -> MemoryObject:
        if key in self._db:
            raw = self._db[key]
            # merge aliases (avoid duplicates)
            existing_aliases = raw.get("entity", {}).get("aliases", []) or []
            merged = list(dict.fromkeys([*existing_aliases, *aliases]))
            raw["entity"]["aliases"] = merged
            self._db[key] = raw
            return self._from_dict(raw)

        mem = MemoryObject(
            id=f"mem_{uuid.uuid4().hex[:12]}",
            entity=EntityRef(type=entity_type, canonical=canonical, aliases=aliases),
            facts={},
            meta={"created_at": datetime.now().astimezone().isoformat()},
        )
        return mem

    def _from_dict(self, d: Dict[str, Any]) -> MemoryObject:
        entity = d.get("entity", {})
        return MemoryObject(
            id=d.get("id", f"mem_{uuid.uuid4().hex[:12]}"),
            entity=EntityRef(
                type=entity.get("type", "unknown"),
                canonical=entity.get("canonical", "unknown"),
                aliases=entity.get("aliases", []) or [],
            ),
            facts=d.get("facts", {}) or {},
            meta=d.get("meta", {}) or {},
        )

    def _split_slot(self, slot: str) -> Tuple[str, str]:
        slot = normalize_text(slot).replace(" ", "")
        if "." not in slot:
            # allow shorthand like "location" => location.current
            return slot, "current"
        group, leaf = slot.split(".", 1)
        return group, leaf

    def _find_best_key(self, entity_raw: str) -> Optional[str]:
        """
        Cheap alias + token overlap search over index.
        """
        idx = self.memory_index()
        query = normalize_text(entity_raw)
        q_tokens = set(query.split())

        best_key = None
        best_score = 0.0

        for row in idx:
            aliases = [normalize_text(a) for a in row.get("aliases", [])]
            ent = normalize_text(row.get("entity") or "")
            candidates = [ent, *aliases]

            score = 0.0
            for c in candidates:
                if not c:
                    continue
                if c == query:
                    score = max(score, 1.0)
                c_tokens = set(c.split())
                if q_tokens and c_tokens:
                    jacc = len(q_tokens & c_tokens) / max(1, len(q_tokens | c_tokens))
                    score = max(score, jacc)

            if score > best_score:
                best_score = score
                best_key = row["key"]

        # threshold to avoid random matches
        if best_score >= 0.34:
            return best_key
        return None
    
def read_fact_with_history(self, entity_raw: str, slot: str):
    value, meta = self.read_fact(entity_raw=entity_raw, slot=slot)
    if meta.get("status") != "ok":
        return None, [], meta

    key = meta["key"]
    obj = self._db[key]
    group, leaf = self._split_slot(slot)
    group_val = obj.get("facts", {}).get(group, {})
    history = group_val.get("history", []) if isinstance(group_val, dict) else []
    return value, history, meta