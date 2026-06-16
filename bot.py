import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est connecté !")

@bot.event
async def on_member_join(member):
    channel_arrivees = discord.utils.get(member.guild.channels, name="arrivées🛬")
    if channel_arrivees:
        embed = discord.Embed(
            description=f"Bienvenue {member.mention} sur le serveur !",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel_arrivees.send("@everyone", embed=embed)

    channel_general = discord.utils.get(member.guild.channels, name="💬-général")
    if channel_general:
        await channel_general.send(f"{member.mention} a rejoint le serveur ! Nous sommes maintenant **{member.guild.member_count}** membres !")
    
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.channels, name="départs🛫")
    if channel:
        await channel.send(f"**{member.name}** a quitté le serveur.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, nombre: int):
    await ctx.channel.purge(limit=nombre + 1)
    await ctx.send(f"✅ {nombre} messages supprimés !", delete_after=3)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, membre: discord.Member, *, raison="Aucune raison donnée"):
    await membre.ban(reason=raison)
    await ctx.send(f"🔨 {membre.name} a été banni. Raison : {raison}")

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ouvrir un ticket", emoji="🎫", style=discord.ButtonStyle.secondary)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await guild.create_text_channel(
            f"ticket-{interaction.user.name}",
            overwrites=overwrites
        )
        await channel.send(f"{interaction.user.mention} Ton ticket est ouvert ! Un membre du support va t'aider.")
        await interaction.response.send_message(f"✅ Ticket créé : {channel.mention}", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    salon = discord.utils.get(ctx.guild.channels, name="🎟️-ticket")
    embed = discord.Embed(
        title="🎫 Support — Ouvrir un ticket",
        description="Cliquez ci-dessous pour ouvrir un ticket.\nUn membre du support vous répondra rapidement.",
        color=discord.Color.blurple()
    )
    await salon.send(embed=embed, view=TicketButton())
    await ctx.send("✅ Message de ticket envoyé !", delete_after=3)
@bot.command()
@commands.has_permissions(administrator=True)
async def fermer(ctx):
    if "ticket-" in ctx.channel.name:
        await ctx.send("🔒 Ticket fermé, suppression dans 5 secondes...")
        import asyncio
        await asyncio.sleep(5)
        await ctx.channel.delete()
    else:
        await ctx.send("❌ Cette commande ne peut être utilisée que dans un ticket !")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_reglement(ctx):
    salon = discord.utils.get(ctx.guild.channels, name="rules")
    embed = discord.Embed(
        title="🏰 Bienvenue sur Clover 🏰",
        description="""Ici, tout le monde commence au rang Class D. Plus tu es actif et impliqué dans le serveur, plus tu as de chances de monter en grade.

📈 **Comment évoluer ?**
⚪ **Class D** → Rang de départ pour tous les nouveaux membres.
🟢 **Class C** → Accessible aux membres qui commencent à se démarquer par leur activité.
🟡 **Class B** → Réservé aux membres actifs et investis dans la communauté.
🔵 **Class A** → Nécessite l'accord d'au moins 1 Class S.
🟣 **Semi Class S** → Nécessite l'accord d'au moins 2 Class S.
🔴 **Class S** → Rang d'élite réservé aux membres les plus méritants, les plus actifs et les plus respectés du serveur.
👑 **Empereur Mage** → Le plus haut rang de Clover. Seul l'Empereur Mage peut décider qui est digne de rejoindre ce rang.

⚠️ Les places dans les hauts rangs sont limitées afin de conserver leur prestige. Cependant, à mesure que le serveur grandira, davantage de places pourront être ouvertes.""",
        color=discord.Color.gold()
    )
    embed.set_image(url="https://i.imgur.com/h23tiKP.jpeg")
    await salon.send(embed=embed)
    
import os
bot.run(os.environ.get("TOKEN"))
