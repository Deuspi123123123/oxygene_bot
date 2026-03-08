import discord
from discord.ext import commands
import asyncio

EMOJI_BRONZE = ":O2_Beonze:"
EMOJI_SILVER = ":O2_Silver:"
EMOJI_GOLD = ":O2_gold:"

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

ROLE_INFO = {

"Comet":{"cat":"contri1","emoji":EMOJI_BRONZE,
"commands":["move vocal"],
"click":["move vocal"],
"access":["vocaux membres"],
"limit":"2 par 10 minutes"},

"Lune":{"cat":"contri1","emoji":EMOJI_BRONZE,
"commands":["=vc","=stats","=help","=member","=user"],
"click":["aucun"],
"access":["outils membres"],
"limit":"aucune"},

"Soleil":{"cat":"contri1","emoji":EMOJI_BRONZE,
"commands":["/rank","/rankup"],
"click":["aucun"],
"access":["outils staff"],
"limit":"rank max Perm III"},

"Saturne":{"cat":"contri2","emoji":EMOJI_SILVER,
"commands":["=warn"],
"click":["mute vocal"],
"access":["vocaux staff"],
"limit":"5 par 10 minutes"},

"ECLIPSE":{"cat":"contri2","emoji":EMOJI_SILVER,
"commands":["/rank","/rankup"],
"click":["mute casque"],
"access":["vocaux staff"],
"limit":"rank max étoile 2"},

"Crown":{"cat":"contri2","emoji":EMOJI_SILVER,
"commands":["/rank","/rankup","/derank","=join","/to","/unto"],
"click":["mute casque"],
"access":["vocaux staff"],
"limit":"rank max étoile 1"},

"blackhole":{"cat":"contri2","emoji":EMOJI_SILVER,
"commands":["=ban"],
"click":["mute vocal","deconnexion vocal"],
"access":["vocaux staff"],
"limit":"3 bans par heure"},

"ADMIN":{"cat":"contri3","emoji":EMOJI_GOLD,
"commands":["=clear","=listmute","=blr","=unblr"],
"click":["timeout","ban","mute"],
"access":["salons admin"],
"limit":"aucune"},

"WORLD":{"cat":"contri3","emoji":EMOJI_GOLD,
"commands":["=ban","/derank"],
"click":["ban"],
"access":["salons admin"],
"limit":"5 bans par heure"},

"Créateur":{"cat":"contri3","emoji":EMOJI_GOLD,
"commands":["=lockname","=bl","=unbl"],
"click":["gestion salons"],
"access":["salons admin"],
"limit":"aucune"}
}


CATEGORY_TEXT = {

"contri1":
"Contribution niveau I. Ton activité commence à être visible. Continue d’aider et monte en influence.",

"contri2":
"Contribution niveau II. Ton statut montre un vrai impact dans le serveur. Tes actions influencent les membres.",

"contri3":
"Contribution niveau III. Cercle interne du serveur. Tes décisions participent directement à la structure du serveur."
}


class RoleInfoDM(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.pending_roles = {}


    async def send_dm(self, member):

        await asyncio.sleep(2)

        roles = self.pending_roles.pop(member.id, [])

        embed = discord.Embed(
            title="Guide de tes nouveaux rôles",
            description="Tes permissions viennent d’être mises à jour sur O².",
            color=0x5865F2
        )

        embed.set_author(name=str(member), icon_url=member.display_avatar.url)

        categories = set()

        for role in roles:

            data = ROLE_INFO.get(role.name)

            if not data:
                continue

            categories.add(data["cat"])

            commands = "\n".join(data["commands"])
            click = "\n".join(data["click"])
            access = "\n".join(data["access"])

            value = f"""
Commandes
{commands}

Clique droit
{click}

Accès
{access}

Limites
{data["limit"]}
"""

            embed.add_field(
                name=f"{data['emoji']} {role.name}",
                value=value,
                inline=False
            )

        if len(embed.fields) == 0:
            return

        intro = ""

        for cat in categories:
            intro += CATEGORY_TEXT.get(cat,"") + "\n\n"

        embed.description = intro

        embed.set_footer(text="Système automatique O²")

        try:
            await member.send(embed=embed)
        except:
            pass


    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        before_roles = set(before.roles)
        after_roles = set(after.roles)

        new_roles = after_roles - before_roles

        roles = [r for r in new_roles if r.id not in IGNORED_ROLES]

        if not roles:
            return

        if after.id not in self.pending_roles:
            self.pending_roles[after.id] = []
            self.bot.loop.create_task(self.send_dm(after))

        self.pending_roles[after.id].extend(roles)


async def setup(bot):
    await bot.add_cog(RoleInfoDM(bot))