from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class HistoryEntry:
    value: Any
    at: str  # ISO 8601
    source: str = "user"
    confidence: float = 1.0


@dataclass
class EntityRef:
    type: str  # e.g. "item", "person", "place"
    canonical: str  # e.g. "wallet"
    aliases: List[str] = field(default_factory=list)


@dataclass
class MemoryObject:
    """
    One memory per entity. Facts are stored in well-known slots, e.g.
    facts["location"]["current"] = "kitchen shelf"
    """
    id: str
    entity: EntityRef
    facts: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        now = datetime.now().astimezone().isoformat()
        self.meta["updated_at"] = now
        self.meta.setdefault("created_at", now)