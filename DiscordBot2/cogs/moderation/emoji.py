import re
import aiohttp
import asyncio
import discord
from discord.ext import commands

FONDATEUR = "Fondateur"

class Emoji(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def addemoji(self, ctx, emoji: discord.PartialEmoji):

        if FONDATEUR not in [r.name for r in ctx.author.roles]:
            return await ctx.send("Permission refusée.")

        if not emoji.url:
            return await ctx.send("Emoji invalide.")

        async with aiohttp.ClientSession() as session:
            async with session.get(str(emoji.url)) as resp:

                if resp.status != 200:
                    return await ctx.send("Impossible de récupérer l'emoji.")

                data = await resp.read()

        new = await ctx.guild.create_custom_emoji(
            name=emoji.name,
            image=data,
            reason=f"Ajout par {ctx.author}"
        )

        await ctx.send(f"Emoji ajouté : {new}")


    @commands.command()
    async def delemoji(self, ctx, emoji: discord.Emoji):

        if FONDATEUR not in [r.name for r in ctx.author.roles]:
            return await ctx.send("Permission refusée.")

        name = emoji.name
        await emoji.delete(reason=f"Supprimé par {ctx.author}")

        await ctx.send(f"Emoji supprimé : {name}")


    @commands.command()
    async def addemojiall(self, ctx):

        if FONDATEUR not in [r.name for r in ctx.author.roles]:
            return await ctx.send("Permission refusée.")

        emojis = re.findall(r"<a?:\w+:\d+>", ctx.message.content)

        if not emojis:
            return await ctx.send("Aucun emoji trouvé.")

        total = len(emojis)
        added = 0

        progress_msg = await ctx.send("Ajout des emojis... 0%")

        async with aiohttp.ClientSession() as session:

            for i, e in enumerate(emojis):

                emoji = discord.PartialEmoji.from_str(e)

                try:
                    async with session.get(str(emoji.url)) as resp:

                        if resp.status != 200:
                            continue

                        data = await resp.read()

                    await ctx.guild.create_custom_emoji(
                        name=emoji.name,
                        image=data,
                        reason=f"Ajout multiple par {ctx.author}"
                    )

                    added += 1

                except:
                    pass

                percent = int(((i + 1) / total) * 100)

                try:
                    await progress_msg.edit(
                        content=f"Ajout des emojis... {percent}% ({i+1}/{total})"
                    )
                except:
                    pass

                await asyncio.sleep(0.4)

        await progress_msg.edit(content=f"Terminé. {added}/{total} emojis ajoutés.")

        await asyncio.sleep(3)

        try:
            await progress_msg.delete()
        except:
            pass


async def setup(bot):
    await bot.add_cog(Emoji(bot))