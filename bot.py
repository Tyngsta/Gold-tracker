import discord
import requests
import asyncio
import os
from datetime import datetime
from discord import app_commands

# =========================
# ENVIRONMENT VARIABLES
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
GOLD_API_KEY = os.getenv("GOLD_API_KEY")
UPDATE_INTERVAL = 1800  # 30 minutes

# =========================
# CLIENT SETUP
# =========================

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# =========================
# GOLD PRICE FUNCTION
# =========================

def get_gold_price():
    try:
        url = "https://www.goldapi.io/api/XAU/EGP"
        headers = {
            "x-access-token": GOLD_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        ounce_price = data["price"]
        gram_price = ounce_price / 31.1035
        buy_price = gram_price * 1.02
        sell_price = gram_price * 0.98
        return ounce_price, gram_price, buy_price, sell_price
    except Exception as e:
        print("Price API Error:", e)
        return None

# =========================
# EMBED CREATOR (TABLE STYLE)
# =========================

def create_gold_embed():
    prices = get_gold_price()
    if not prices:
        return discord.Embed(title="🪙 Gold Prices", description="Failed to fetch prices.", color=0xFF0000)

    ounce, gram, buy, sell = prices

    # Gram prices
    grams_labels = ["1g", "5g", "10g", "20g"]
    grams_buy = [buy, buy*5, buy*10, buy*20]
    grams_sell = [sell, sell*5, sell*10, sell*20]

    # 1oz price
    buy_1oz = buy * 31.1035
    sell_1oz = sell * 31.1035

    # Create table string
    table = "Unit  |  Buy ($)   |  Sell ($)\n"
    table += "----------------------------\n"
    for label, b, s in zip(grams_labels, grams_buy, grams_sell):
        table += f"{label:<5} | {b:>8.2f} | {s:>8.2f}\n"
    table += f"1oz   | {buy_1oz:>8.2f} | {sell_1oz:>8.2f}"

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")

    embed = discord.Embed(title="🪙 Gold Market Update", color=0xFFD700)
    embed.add_field(name="Prices", value=f"```{table}```", inline=False)
    embed.set_footer(text=f"Data fetched on {date_str} | Updates every 30 minutes")

    return embed

# =========================
# BACKGROUND LOOP
# =========================

async def gold_price_loop():
    await client.wait_until_ready()
    print("Gold price loop started")

    while True:
        try:
            channel = await client.fetch_channel(CHANNEL_ID)
            embed = create_gold_embed()
            await channel.send(embed=embed)
            print("Gold update sent")
        except Exception as e:
            print("Bot Error:", e)

        await asyncio.sleep(UPDATE_INTERVAL)

# =========================
# SLASH COMMAND
# =========================

@tree.command(name="gold", description="Get current gold prices", guild=discord.Object(id=GUILD_ID))
async def gold_command(interaction: discord.Interaction):
    embed = create_gold_embed()
    await interaction.response.send_message(embed=embed)

# =========================
# BOT READY EVENT
# =========================

@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")
    client.loop.create_task(gold_price_loop())
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Slash commands synced.")

# =========================
# START BOT
# =========================

client.run(TOKEN)
