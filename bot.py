import os

import scrape
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(
        f'{bot.user} is connected'
    )

@bot.command(name='pos')
async def findPosition(ctx, url, nick, score):
    await ctx.send(scrape.main(["", url, nick, score]))

bot.run(TOKEN)