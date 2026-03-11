import discord
import requests
import asyncio
import os
from datetime import datetime
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
GOLD_API_KEY = os.getenv("GOLD_API_KEY")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
GUILD_ID = int(os.getenv("GUILD_ID"))

UPDATE_INTERVAL = 1800

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def get_gold_price():
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {"x-access-token": GOLD_API_KEY}
    r = requests.get(url, headers=headers)
    data = r.json()

    ounce = data["price"]
    gram = ounce / 31.1035

    buy = gram * 1.02
    sell = gram * 0.98

    return ounce, gram, buy, sell

def create_embed():
    ounce, gram, buy, sell = get_gold_price()

    embed = discord.Embed(
        title="🪙 Gold Market Update",
        color=0xFFD700
    )

    embed.add_field(
        name="Spot Price",
        value=f"1oz: ${ounce:.2f}\n1g: ${gram:.2f}",
        inline=False
    )

    embed.set_footer(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return embed

async def price_loop():
    await client.wait_until_ready()

    while True:
        channel = await client.fetch_channel(CHANNEL_ID)
        await channel.send(embed=create_embed())
        await asyncio.sleep(UPDATE_INTERVAL)

@tree.command(name="gold", description="Get current gold prices", guild=discord.Object(id=GUILD_ID))
async def gold(interaction: discord.Interaction):
    await interaction.response.send_message(embed=create_embed())

@client.event
async def on_ready():
    print("Bot online")
    client.loop.create_task(price_loop())
    await tree.sync(guild=discord.Object(id=GUILD_ID))

client.run(TOKEN)
