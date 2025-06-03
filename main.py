
import discord
from discord.ext import commands
from discord.ui import Modal, InputText, View, Button
from discord import Embed, ButtonStyle
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
PAINEL_CHANNEL_ID = int(os.getenv("PAINEL_CHANNEL_ID"))
REGISTRO_LOG_CHANNEL_ID = int(os.getenv("REGISTRO_LOG_CHANNEL_ID"))
CARGO_APROVADO_ID = int(os.getenv("CARGO_APROVADO_ID"))
CARGO_NEGADO_ID = int(os.getenv("CARGO_NEGADO_ID"))

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

class RegistroModal(Modal):
    def __init__(self):
        super().__init__(title="Formulário de Registro")
        self.add_item(InputText(label="Nick Ingame", placeholder="Ex: Tulio"))
        self.add_item(InputText(label="ID do Jogo", placeholder="Ex: 586"))
        self.add_item(InputText(label="Telefone do Jogo", placeholder="Ex: 852159"))
        self.add_item(InputText(label="ID do Recrutador", placeholder="Ex: 236"))

    async def callback(self, interaction: discord.Interaction):
        nick, id_jogo, telefone, id_recrutador = [item.value for item in self.children]
        user = interaction.user

        embed = Embed(title="🌾 Novo Pedido de Registro", color=discord.Color.orange())
        embed.add_field(name="🧍 Nick Ingame", value=nick, inline=False)
        embed.add_field(name="🆔 ID do Jogo", value=id_jogo, inline=True)
        embed.add_field(name="📞 Telefone do Jogo", value=telefone, inline=True)
        embed.add_field(name="🎯 ID do Recrutador", value=id_recrutador, inline=False)
        embed.set_footer(text=f"Solicitante: {user.name} | ID: {user.id} • Hoje às {interaction.created_at.strftime('%H:%M')}")

        view = View()

        async def aprovado_callback(i):
            await i.response.defer()
            membro = i.guild.get_member(user.id)
            if membro:
                await membro.add_roles(i.guild.get_role(CARGO_APROVADO_ID))
                await membro.edit(nick=f"{id_jogo} | {nick}")
            embed.color = discord.Color.green()
            embed.add_field(name="✅ Aprovado por", value=f"{i.user.mention} • {discord.utils.format_dt(i.created_at, style='f')}", inline=False)
            await i.message.edit(embed=embed, view=None)

        async def negado_callback(i):
            await i.response.defer()
            membro = i.guild.get_member(user.id)
            if membro:
                await membro.add_roles(i.guild.get_role(CARGO_NEGADO_ID))
            embed.color = discord.Color.red()
            embed.add_field(name="❌ Negado por", value=f"{i.user.mention} • {discord.utils.format_dt(i.created_at, style='f')}", inline=False)
            await i.message.edit(embed=embed, view=None)

        view.add_item(Button(label="Aprovar", style=ButtonStyle.success, custom_id="aprovar"))
        view.add_item(Button(label="Negar", style=ButtonStyle.danger, custom_id="negar"))

        msg = await bot.get_channel(REGISTRO_LOG_CHANNEL_ID).send(embed=embed, view=view)

        @bot.event
        async def on_interaction(inter):
            if inter.type == discord.InteractionType.component and inter.message.id == msg.id:
                if inter.data["custom_id"] == "aprovar":
                    await aprovado_callback(inter)
                elif inter.data["custom_id"] == "negar":
                    await negado_callback(inter)

        await interaction.response.send_message("Formulário enviado com sucesso!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    canal = bot.get_channel(PAINEL_CHANNEL_ID)
    embed = Embed(
        title="**Bem-vindo(a) ao Talibã! 🎉**",
        description=(
            "Para acessar todos os recursos, preencha o formulário de registro clicando no botão abaixo. "
            "Assim que um moderador revisar suas informações, sua entrada será liberada.
"
            "Se tiver dúvidas, sinta-se à vontade para perguntar."
        ),
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1372590882460536893/1379224722981654569/d6088td-2c6ef079-b2db-44fb-9002-a68872ba2b55.jpg")
    view = View()
    view.add_item(Button(label="Registrar", style=ButtonStyle.primary, custom_id="open_modal"))

    async def painel_interaction(interaction):
        if interaction.data["custom_id"] == "open_modal":
            await interaction.response.send_modal(RegistroModal())

    await canal.purge()
    await canal.send(embed=embed, view=view)

    @bot.event
    async def on_interaction(interaction):
        if interaction.type == discord.InteractionType.component and interaction.data["custom_id"] == "open_modal":
            await painel_interaction(interaction)

bot.run(TOKEN)
