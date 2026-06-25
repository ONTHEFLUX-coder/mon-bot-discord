import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    bot.add_view(TicketButton())
    print(f"✅ {bot.user} est connecté !")

@bot.event
async def on_member_join(member):
    channel_arrivees = discord.utils.get(member.guild.channels, name="arrivées🛬")
    if channel_arrivees:
        embed = discord.Embed(
            description=f"Bienvenue {member.mention} sur le serveur ! 🎉\nNous sommes maintenant **{member.guild.member_count}** membres !",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel_arrivees.send(embed=embed)
    
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

    @discord.ui.button(label="Ouvrir un ticket", emoji="🎫", style=discord.ButtonStyle.secondary, custom_id="open_ticket")
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
        await channel.send(f"{interaction.user.mention} Ton ticket est ouvert ! 🎫")
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
    
@bot.event
async def on_member_update(before, after):
    hierarchie = ["Class D", "Class C", "Class B", "Class A", "Semi Class S", "Class S", "Empreur mage👑"]
    
    if before.roles != after.roles:
        salon = discord.utils.get(after.guild.channels, name="📈rôles")
        if not salon:
            return
        
        roles_avant = set(r.name for r in before.roles if r.name in hierarchie)
        roles_apres = set(r.name for r in after.roles if r.name in hierarchie)
        
        roles_ajoutes = roles_apres - roles_avant
        roles_retires = roles_avant - roles_apres
        
        for role_obtenu in roles_ajoutes:
            for role_perdu in roles_retires:
                index_avant = hierarchie.index(role_perdu)
                index_apres = hierarchie.index(role_obtenu)
                
                if index_apres > index_avant:
                    embed = discord.Embed(
                        description=f"🎉 Félicitations {after.mention} ! Tu es passé(e) de **{role_perdu}** à **{role_obtenu}** !",
                        color=discord.Color.green()
                    )
                else:
                    embed = discord.Embed(
                        description=f"💔 Dommage {after.mention}, tu es passé(e) de **{role_perdu}** à **{role_obtenu}**.",
                        color=discord.Color.red()
                    )
                await salon.send(embed=embed)
                
@bot.command()
async def ngl(ctx):
    if ctx.channel.name == "👀-messages-anonymes":
        await ctx.send("https://ngl.link/enevo95")

@bot.command()
async def avatar(ctx, membre: discord.Member = None):
    if membre is None:
        membre = ctx.author
    embed = discord.Embed(
        title=f"Avatar de {membre.name}",
        color=discord.Color.blurple()
    )
    embed.set_image(url=membre.display_avatar.url)
    embed.add_field(name="Lien", value=f"[Clique ici]({membre.display_avatar.url})")
    await ctx.send(embed=embed)

@bot.command()
async def banner(ctx, membre: discord.Member = None):
    if membre is None:
        membre = ctx.author
    user = await bot.fetch_user(membre.id)
    if user.banner:
        embed = discord.Embed(
            title=f"Bannière de {membre.name}",
            color=discord.Color.blurple()
        )
        embed.set_image(url=user.banner.url)
        embed.add_field(name="Lien", value=f"[Clique ici]({user.banner.url})")
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ {membre.name} n'a pas de bannière !")

@bot.event
async def on_voice_state_update(member, before, after):
    salon = discord.utils.get(member.guild.channels, name="logs-vocaux")
    if not salon:
        return

    import asyncio
    await asyncio.sleep(1)

    # Mute serveur
    if before.mute != after.mute:
        moderateur = "Inconnu"
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
            if entry.target.id == member.id:
                moderateur = entry.user.mention
        if after.mute:
            embed = discord.Embed(description=f"🔇 {member.mention} a été **mis en sourdine** par {moderateur}", color=discord.Color.red())
        else:
            embed = discord.Embed(description=f"🔊 {member.mention} a été **retiré de la sourdine** par {moderateur}", color=discord.Color.green())
        await salon.send(embed=embed)

    # Deaf serveur
    if before.deaf != after.deaf:
        moderateur = "Inconnu"
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
            if entry.target.id == member.id:
                moderateur = entry.user.mention
        if after.deaf:
            embed = discord.Embed(description=f"🙉 {member.mention} a été **mute** par {moderateur}", color=discord.Color.red())
        else:
            embed = discord.Embed(description=f"👂 {member.mention} a été **demute** par {moderateur}", color=discord.Color.green())
        await salon.send(embed=embed)

    # Déplacement
  if before.channel and after.channel and before.channel != after.channel:
    moderateur = None
    async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_move):
        if entry.target.id == member.id:
            moderateur = entry.user
    if moderateur and moderateur.id != member.id:
        embed = discord.Embed(
            description=f"➡️ {member.mention} a été **déplacé** de **{before.channel.name}** vers **{after.channel.name}** par {moderateur.mention}",
            color=discord.Color.blue()
        )
        await salon.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def deban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ {user.name} a été débanni !")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, membre: discord.Member, *, raison="Aucune raison donnée"):
    role_mute = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role_mute:
        role_mute = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role_mute, send_messages=False, speak=False)
    await membre.add_roles(role_mute)
    await ctx.send(f"🔇 {membre.mention} a été mute. Raison : {raison}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, membre: discord.Member):
    role_mute = discord.utils.get(ctx.guild.roles, name="Muted")
    if role_mute in membre.roles:
        await membre.remove_roles(role_mute)
        await ctx.send(f"🔊 {membre.mention} a été unmute !")
    else:
        await ctx.send(f"❌ {membre.mention} n'est pas mute !")
                    
import os
bot.run(os.environ.get("TOKEN"))
