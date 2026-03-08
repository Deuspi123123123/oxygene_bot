import discord
from discord.ext import commands
import time

FONDATEUR = "Fondateur"
COOLDOWN = 300

cooldowns = {}


class ConfirmReset(discord.ui.View):

    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx

    @discord.ui.button(label="Confirmer le reset", style=discord.ButtonStyle.red, emoji="⚠️")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(
                "Seul l'auteur de la commande peut confirmer.",
                ephemeral=True
            )

        channel = self.ctx.channel
        guild = self.ctx.guild

        category = channel.category
        position = channel.position

        new_channel = await channel.clone()

        await new_channel.edit(
            position=position,
            category=category
        )

        await interaction.response.send_message("Salon réinitialisé.", ephemeral=True)

        logs = self.ctx.bot.get_cog("Logs")

        if logs:

            embed = discord.Embed(
                title="Reset de salon",
                color=discord.Color.orange()
            )

            embed.add_field(
                name="Salon",
                value=channel.name,
                inline=False
            )

            embed.add_field(
                name="Staff",
                value=f"{interaction.user.mention} ({interaction.user.id})",
                inline=False
            )

            embed.timestamp = discord.utils.utcnow()

            await logs.send_log(guild, "mod_logs", embed)

        await channel.delete()

        embed = discord.Embed(
            description="Salon recréé avec succès.",
            color=discord.Color.green()
        )

        await new_channel.send(embed=embed)

        self.stop()

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(
                "Seul l'auteur peut annuler.",
                ephemeral=True
            )

        await interaction.response.edit_message(
            content="Reset annulé.",
            view=None
        )

        self.stop()


class ResetChannel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reset(self, ctx):

        if FONDATEUR not in [r.name for r in ctx.author.roles]:
            return

        now = time.time()

        if ctx.author.id in cooldowns:

            ts = cooldowns[ctx.author.id]

            if now - ts < COOLDOWN:

                remaining = int(COOLDOWN - (now - ts))

                return await ctx.send(
                    f"Cooldown actif. Réessaie dans {remaining} secondes."
                )

        cooldowns[ctx.author.id] = now

        embed = discord.Embed(
            title="Confirmation requise",
            description=(
                "Cette action va réinitialiser entièrement ce salon.\n"
                "Tous les messages seront supprimés."
            ),
            color=discord.Color.red()
        )

        embed.set_footer(text="Confirmation requise")

        await ctx.send(embed=embed, view=ConfirmReset(ctx))


async def setup(bot):
    await bot.add_cog(ResetChannel(bot))