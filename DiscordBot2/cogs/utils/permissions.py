from discord.ext import commands
from database import has_custom_permission


def require_permission(command_name, roles=None):
    roles = roles or []

    async def predicate(ctx):
        user_roles = [r.name for r in ctx.author.roles]

        # Vérifie rôle
        if any(role in user_roles for role in roles):
            return True

        # Vérifie permission custom
        if has_custom_permission(ctx.author.id, command_name):
            return True

        await ctx.send("Tu n'as pas la permission d'utiliser cette commande.")
        return False

    return commands.check(predicate)