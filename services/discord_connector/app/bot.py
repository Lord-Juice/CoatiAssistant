import os
import discord

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
# Für reine DMs ist das meist nicht nötig; für Server-Message-Content später ggf. aktivieren:
# intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Eingeloggt als {client.user} (id={client.user.id})")

@client.event
async def on_message(message: discord.Message):
    # Nicht auf sich selbst reagieren
    if message.author == client.user:
        return

    # Nur DMs behandeln
    if message.guild is None:
        print(f"📩 DM von {message.author}: {message.content}")
        await message.channel.send(f"Ich habe verstanden: {message.content}")

client.run(TOKEN)
