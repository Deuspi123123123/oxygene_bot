import discord
from discord.ext import commands

class Snipe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sniped_messages = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if message.author.bot:
            return

        self.sniped_messages[message.channel.id] = {
            "content": message.content,
            "author": message.author,
            "avatar": message.author.display_avatar.url
        }
        

    @commands.command()
    @commands.cooldown(3, 3600, commands.BucketType.user)
    async def snipe(self, ctx):

        data = self.sniped_messages.get(ctx.channel.id)

        if not data:
            return await ctx.send("Aucun message supprimé récemment.")

        embed = discord.Embed(
            description=data["content"],
            color=discord.Color.blurple()
        )

        embed.set_author(
            name=data["author"],
            icon_url=data["avatar"]
        )

        embed.set_footer(text=f"Sniped par {ctx.author}")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Snipe(bot))