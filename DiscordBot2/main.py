import discord
from discord.ext import commands
import asyncio
import os
import time
from database import init_db

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="=",
    intents=intents,
    help_command=None
)

command_attempts = {}
command_cooldowns = {}

TOKEN = os.getenv("TOKEN")


@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"Bot connecté : {bot.user}")


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):

    user = ctx.author.id
    now = time.time()

    if user in command_cooldowns:
        if now < command_cooldowns[user]:
            return

    if isinstance(error, commands.CommandNotFound):

        attempts = command_attempts.get(user, 0) + 1
        command_attempts[user] = attempts

        if attempts >= 3:
            command_cooldowns[user] = now + 60
            command_attempts[user] = 0
            await ctx.send("Trop de tentatives. Réessaie plus tard.")
            return

        await ctx.send("Commande inconnue.")
        return

    print(error)


async def load_cogs():

    for file in os.listdir("cogs/moderation"):

        if file.endswith(".py") and file != "__init__.py":

            cog = f"cogs.moderation.{file[:-3]}"

            try:
                await bot.load_extension(cog)
            except Exception as e:
                print(f"Erreur chargement {cog} : {e}")


async def main():

    init_db()

    async with bot:

        await load_cogs()

        await bot.start("TOKEN")



asyncio.run(main())




