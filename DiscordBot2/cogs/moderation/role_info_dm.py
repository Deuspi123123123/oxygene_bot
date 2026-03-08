import discord
from discord.ext import commands
import asyncio
import os
import re

STRUCTURE_FILE = "roles_structure.txt"

EMOJI_BRONZE = "<:O2_Beonze:1480026906282950707>"
EMOJI_SILVER = "<:O2_Silver:1480027024046428250>"
EMOJI_GOLD = "<:O2_gold:1480027129944215603>"

ICON_COMMAND = "📜"
ICON_CLICK = "🖱"
ICON_ACCESS = "🔐"
ICON_LIMIT = "⚠"

IGNORED_ROLES = [
1467694509147164845,
1479217749304545404,
1479213229719683325,
1479216004986044557,
1479554554985971893,
1479557128820625543,
1479555681756385310,
1479555468006523003,
1479555417351786586,
1479554803838222512,
1479554851901014077,
1479554918384930917,
1479555046793285654,
1479555003361267943
]


class RoleInfoDM(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.pending_roles = {}
        self.structure = self.load_structure()


    def load_structure(self):

        roles = {}

        if not os.path.exists(STRUCTURE_FILE):
            print("roles_structure.txt introuvable")
            return roles

        with open(STRUCTURE_FILE, "r", encoding="utf-8") as f:
            blocks = f.read().split("────────────────")

        for block in blocks:

            role_id = None
            name = None

            commands = []
            click = []
            access = []
            limits = []

            section = None

            for line in block.splitlines():

                line = line.strip()

                if not line:
                    continue

                if not name:
                    name = line
                    continue

                if line.startswith("ID"):
                    role_id = int(re.findall(r"\d+", line)[0])
                    continue

                if line == "Commandes":
                    section = "commands"
                    continue

                if line == "Click":
                    section = "click"
                    continue

                if line == "Accès":
                    section = "access"
                    continue

                if line == "Limites":
                    section = "limits"
                    continue

                if section == "commands":
                    commands.append(line)

                elif section == "click":
                    click.append(line)

                elif section == "access":
                    access.append(line)

                elif section == "limits":
                    limits.append(line)

            if role_id:
                roles[role_id] = {
                    "name": name,
                    "commands": commands,
                    "click": click,
                    "access": access,
                    "limits": limits
                }

        print("Structure chargée :", len(roles), "roles")
        return roles


    def category_message(self, role_name):

        name = role_name.lower()

        if "tempête" in name or "neige" in name or "vie" in name or "fleures" in name:
            return "**Équipe Oxygène**\nTon rôle évolue selon ton activité vocale."

        if "croissant" in name or "constellation" in name or "vœu" in name:
            return "**Modération O²**\nParticipation à la modération du serveur."

        if "gestion" in name:
            return "**Gestion modération**\nTu aides à gérer les tickets et les abus."

        if "comet" in name or "lune" in name or "soleil" in name:
            return f"{EMOJI_BRONZE} **Contribution niveau I**\nSoutien actif du serveur."

        if "saturne" in name or "eclipse" in name or "crown" in name or "blackhole" in name:
            return f"{EMOJI_SILVER} **Contribution niveau II**\nInfluence croissante sur le serveur."

        if "admin" in name or "world" in name or "créateur" in name:
            return f"{EMOJI_GOLD} **Contribution niveau III**\nCercle interne du serveur."

        if "bot" in name:
            return "**Système BOT**\nRôle technique du serveur."

        return ""


    def build_embed(self, member, roles_data):

        embed = discord.Embed(
            title="Guide de ton nouveau rôle",
            description=f"{member.mention}\nTon rôle vient d'évoluer sur **O²**.\nVoici les permissions associées.",
            color=0x5865F2
        )

        embed.set_author(
            name=str(member),
            icon_url=member.display_avatar.url
        )

        for role_name, data in roles_data.items():

            commands = "\n".join(data["commands"]) if data["commands"] else "aucune"
            click = "\n".join(data["click"]) if data["click"] else "aucun"
            access = "\n".join(data["access"]) if data["access"] else "standard"
            limits = "\n".join(data["limits"]) if data["limits"] else "aucune"

            category = self.category_message(role_name)

            value = f"""
{category}

__Commandes__
{commands}

__Actions__
{click}

__Accès__
{access}

__Limites__
{limits}
"""

            embed.add_field(
                name=f"Rôle : {role_name}",
                value=value,
                inline=False
            )

        embed.set_footer(text="Documentation automatique O²")

        return embed


    async def send_roles_dm(self, member):

        await asyncio.sleep(2)

        role_ids = self.pending_roles.pop(member.id, [])

        roles_data = {}

        for rid in role_ids:

            if rid in self.structure:
                role = self.structure[rid]
                roles_data[role["name"]] = role

        if not roles_data:
            return

        embed = self.build_embed(member, roles_data)

        try:
            await member.send(embed=embed)
        except Exception as e:
            print("DM impossible :", e)


    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        before_roles = {r.id for r in before.roles}
        after_roles = {r.id for r in after.roles}

        new_roles = list(after_roles.difference(before_roles))
        new_roles = [rid for rid in new_roles if rid not in IGNORED_ROLES]

        if not new_roles:
            return

        if after.id not in self.pending_roles:
            self.pending_roles[after.id] = []
            asyncio.create_task(self.send_roles_dm(after))

        self.pending_roles[after.id].extend(new_roles)


async def setup(bot):
    await bot.add_cog(RoleInfoDM(bot))