import os
import random
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()

        print(f"✅ {len(synced)} comandos / sincronizados.")

        for comando in synced:
            print(f"➡️ /{comando.name}")

        # Prepara automaticamente o canal de logs.
        await preparar_canal_logs()

        # Sincroniza o contador ao iniciar (inclusive após reinicializações).
        for guild in bot.guilds:
            await atualizar_contador(guild)

    except Exception as erro:
        print(f"❌ Erro ao sincronizar: {erro}")


@bot.tree.command(name="ping", description="Mostra a latência do bot.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🏓 Pong! `{round(bot.latency * 1000)}ms`"
    )


@bot.tree.command(name="avatar", description="Mostra o avatar de um usuário.")
@app_commands.describe(usuario="Usuário que você deseja visualizar")
async def avatar(
    interaction: discord.Interaction,
    usuario: discord.Member = None
):
    usuario = usuario or interaction.user

    embed = discord.Embed(
        title=f"🖼️ Avatar de {usuario.display_name}",
        color=discord.Color.purple()
    )

    embed.set_image(url=usuario.display_avatar.url)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="serverinfo", description="Mostra informações do servidor.")
async def serverinfo(interaction: discord.Interaction):

    guild = interaction.guild

    embed = discord.Embed(
        title=f"📊 {guild.name}",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="👥 Membros",
        value=guild.member_count,
        inline=True
    )

    embed.add_field(
        name="👑 Dono",
        value=guild.owner.mention if guild.owner else "Desconhecido",
        inline=True
    )

    embed.add_field(
        name="🆔 ID",
        value=guild.id,
        inline=False
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await interaction.response.send_message(embed=embed)


# =========================
# BOAS-VINDAS
# =========================

CANAL_BOAS_VINDAS = 1555761617524887562
CANAL_CONTADOR = 1555762204924452924

async def atualizar_contador(guild):
    # Primeiro procura no cache; se necessário, consulta o Discord pela API.
    canal = guild.get_channel(CANAL_CONTADOR)

    if canal is None:
        try:
            canal = await bot.fetch_channel(CANAL_CONTADOR)
        except discord.NotFound:
            print(f"❌ Canal do contador {CANAL_CONTADOR} não encontrado. Confira o ID.")
            return
        except discord.Forbidden:
            print("❌ O bot não tem acesso ao canal do contador.")
            return
        except discord.HTTPException as erro:
            print(f"❌ Não foi possível buscar o canal do contador: {erro}")
            return

    if not hasattr(canal, "edit") or not hasattr(canal, "name"):
        print("❌ O ID do contador não corresponde a um canal editável.")
        return

    quantidade = guild.member_count
    if quantidade is None:
        try:
            quantidade = (await guild.fetch_member_count())
        except (AttributeError, discord.HTTPException):
            print("❌ Não foi possível obter a quantidade atual de membros.")
            return

    novo_nome = f"👥 Membros: {quantidade}"

    try:
        if canal.name != novo_nome:
            await canal.edit(name=novo_nome, reason="Atualização automática do contador de membros")
            print(f"✅ Contador atualizado: {novo_nome}")
    except discord.Forbidden:
        print("❌ O bot não tem permissão para editar o canal do contador. Verifique Gerenciar canais.")
    except discord.HTTPException as erro:
        print(f"❌ Erro ao atualizar o contador: {erro}")

@bot.event
async def on_member_join(member):
    await atualizar_contador(member.guild)
        # 🎭 Cargo automático
    cargo = member.guild.get_role(1555760706895482971)


    if cargo:
        try:
            await member.add_roles(
                cargo,
                reason="Cargo automático ao entrar no servidor"
            )
            print(f"✅ Cargo automático dado para {member}")
        except discord.Forbidden:
            print("❌ O bot não tem permissão para dar o cargo.")
        except Exception as erro:
            print(f"❌ Erro no autorole: {erro}")
    else:
        print("❌ Cargo do autorole não encontrado.") 
    
    # Busca o canal pelo ID; se não estiver no cache, tenta buscar pela API.
    canal = bot.get_channel(CANAL_BOAS_VINDAS)
    if canal is None:
        try:
            canal = await bot.fetch_channel(CANAL_BOAS_VINDAS)
        except discord.NotFound:
            print(f"❌ Canal de boas-vindas {CANAL_BOAS_VINDAS} não encontrado. Confira o ID.")
            return
        except discord.Forbidden:
            print("❌ O bot não tem acesso ao canal de boas-vindas.")
            return
        except discord.HTTPException as erro:
            print(f"❌ Não foi possível buscar o canal de boas-vindas: {erro}")
            return

    if not hasattr(canal, "send"):
        print("❌ O ID configurado para boas-vindas não é um canal que aceita mensagens.")
        return
    mensagens_boas_vindas = [
    f"🖤 {member.mention} acabou de chegar na **Community Originais**. Seja bem-vindo(a)!",
    f"👑 Abram espaço! {member.mention} chegou nos **Originais**.",
    f"🔥 Mais um Original na área! Salve, {member.mention}!",
    f"🥷 {member.mention} apareceu por aqui... seja bem-vindo(a) aos **Originais**.",
    f"⚡ Reforço chegando! Bem-vindo(a), {member.mention}!",
    f"🎉 Recebam {member.mention}! A família **Originais** está crescendo.",
    f"🫡 Salve, {member.mention}! Seja bem-vindo(a) à **Community Originais**.",
    f"💀 Atenção: {member.mention} acaba de entrar no território dos **Originais**.",
    f"🚀 {member.mention} entrou no servidor. Aproveite a comunidade!",
    f"🖤 A família cresceu! Bem-vindo(a), {member.mention}.",

    f"🏙️ Novo player na cidade: {member.mention}! Seja bem-vindo(a).",
    f"🚘 {member.mention} acabou de spawnar na **Community Originais**!",
    f"🎮 Player conectado: {member.mention}. Bem-vindo(a) aos **Originais**!",
    f"📡 Conexão estabelecida! {member.mention} entrou no servidor.",
    f"🏁 Chegou mais um! Seja bem-vindo(a), {member.mention}.",
    f"🔑 {member.mention} recebeu acesso à **Community Originais**. Bem-vindo(a)!",
    f"🌃 Mais um pela cidade! Salve, {member.mention}!",
    f"🚨 Novo membro detectado: {member.mention}. Recebam nosso novo Original!",
    f"💨 Do nada apareceu {member.mention} 😂 Seja bem-vindo(a)!",
    f"🎯 {member.mention} encontrou o servidor certo. Bem-vindo(a)!",

    f"👀 Olha quem chegou... {member.mention}!",
    f"😂 Alguém abriu o portão e {member.mention} entrou. Bem-vindo(a)!",
    f"🍷 Chegou com estilo! Bem-vindo(a), {member.mention}.",
    f"🤝 Recebam bem {member.mention}! Agora ele(a) faz parte da comunidade.",
    f"🛬 Pousou nos **Originais**! Bem-vindo(a), {member.mention}!",
    f"✨ Temos companhia nova! Salve, {member.mention}!",
    f"🔔 Ding dong! {member.mention} chegou na **Community Originais**.",
    f"🕶️ Novo Original identificado: {member.mention}. Seja bem-vindo(a)!",
    f"🏆 Seja bem-vindo(a), {member.mention}! Você é o membro **#{member.guild.member_count}**.",
    f"🖤 Bem-vindo(a) à família, {member.mention}. **Uma vez Original, sempre Original.**"
]
    mensagem = random.choice(mensagens_boas_vindas)
    try:
        await canal.send(mensagem)
        print(f"✅ Boas-vindas enviada para {member} no canal #{canal.name}.")
    except discord.Forbidden:
        print("❌ Sem permissão para enviar mensagens no canal de boas-vindas. Confira Ver canal e Enviar mensagens.")
    except discord.HTTPException as erro:
        print(f"❌ Erro ao enviar boas-vindas: {erro}")
@bot.event
async def on_member_remove(member):
    await atualizar_contador(member.guild)

# ==========================================
# 🛡️ SISTEMA DE MODERAÇÃO - OS ORIGINAIS
# ==========================================

from datetime import timedelta


# /clear
@bot.tree.command(name="clear", description="Apaga mensagens do canal.")
@app_commands.describe(quantidade="Quantidade de mensagens para apagar")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, quantidade: int):

    if quantidade < 1 or quantidade > 100:
        await interaction.response.send_message(
            "❌ Escolha uma quantidade entre 1 e 100.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    try:
        apagadas = await interaction.channel.purge(
            limit=quantidade
        )
        await enviar_log_moderacao(
    titulo="🧹 Mensagens apagadas",
    moderador=interaction.user,
    detalhes=(
        f"📍 Canal: {interaction.channel.mention}\n"
        f"🗑️ Quantidade: {len(apagadas)}"
    )
)

        await interaction.followup.send(
            f"🧹 **{len(apagadas)} mensagens foram apagadas!**",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.followup.send(
            "❌ Eu não tenho permissão para apagar mensagens neste canal.",
            ephemeral=True
        )

    except Exception as erro:
        print(f"❌ ERRO NO /CLEAR: {erro}")

        await interaction.followup.send(
            "❌ Ocorreu um erro ao apagar as mensagens. Veja o CMD.",
            ephemeral=True
        )


# /kick
@bot.tree.command(name="kick", description="Expulsa um membro do servidor.")
@app_commands.describe(
    membro="Membro que será expulso",
    motivo="Motivo da expulsão"
)
@app_commands.checks.has_permissions(kick_members=True)
async def kick(
    interaction: discord.Interaction,
    membro: discord.Member,
    motivo: str = "Nenhum motivo informado"
):
    if membro == interaction.user:
        await interaction.response.send_message(
            "❌ Você não pode expulsar você mesmo.",
            ephemeral=True
        )
        return

    try:
        await membro.kick(reason=motivo)
        await enviar_log_moderacao(
    titulo="👢 Membro expulso",
    moderador=interaction.user,
    usuario=membro,
    motivo=motivo
)

        embed = discord.Embed(
            title="👢 Membro expulso",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="👤 Usuário",
            value=f"{membro} (`{membro.id}`)",
            inline=False
        )

        embed.add_field(
            name="🛡️ Moderador",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="📝 Motivo",
            value=motivo,
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Não tenho permissão para expulsar esse membro.",
            ephemeral=True
        )


# /ban
@bot.tree.command(name="ban", description="Bane um membro do servidor.")
@app_commands.describe(
    membro="Membro que será banido",
    motivo="Motivo do banimento"
)
@app_commands.checks.has_permissions(ban_members=True)
async def ban(
    interaction: discord.Interaction,
    membro: discord.Member,
    motivo: str = "Nenhum motivo informado"
):
    if membro == interaction.user:
        await interaction.response.send_message(
            "❌ Você não pode banir você mesmo.",
            ephemeral=True
        )
        return

    try:
        await membro.ban(reason=motivo)
        await enviar_log_moderacao(
    titulo="🔨 Membro banido",
    moderador=interaction.user,
    usuario=membro,
    motivo=motivo
)

        embed = discord.Embed(
            title="🔨 Membro banido",
            color=discord.Color.red()
        )

        embed.add_field(
            name="👤 Usuário",
            value=f"{membro} (`{membro.id}`)",
            inline=False
        )

        embed.add_field(
            name="🛡️ Moderador",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="📝 Motivo",
            value=motivo,
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Não tenho permissão para banir esse membro.",
            ephemeral=True
        )


# /timeout
@bot.tree.command(name="timeout", description="Coloca um membro de castigo.")
@app_commands.describe(
    membro="Membro que receberá timeout",
    minutos="Duração em minutos",
    motivo="Motivo do timeout"
)
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(
    interaction: discord.Interaction,
    membro: discord.Member,
    minutos: int,
    motivo: str = "Nenhum motivo informado"
):
    if minutos < 1 or minutos > 40320:
        await interaction.response.send_message(
            "❌ Escolha entre 1 e 40320 minutos.",
            ephemeral=True
        )
        return

    if membro == interaction.user:
        await interaction.response.send_message(
            "❌ Você não pode aplicar timeout em você mesmo.",
            ephemeral=True
        )
        return

    try:
        await membro.timeout(
            timedelta(minutes=minutos),
            reason=motivo
        )

        # Envia para o canal de logs
        await enviar_log_moderacao(
            titulo="🔇 Timeout aplicado",
            moderador=interaction.user,
            usuario=membro,
            motivo=motivo,
            detalhes=f"⏱️ Duração: {minutos} minutos"
        )

        # Resposta do comando
        embed = discord.Embed(
            title="🔇 Timeout aplicado",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="👤 Usuário",
            value=membro.mention,
            inline=True
        )

        embed.add_field(
            name="⏱️ Tempo",
            value=f"{minutos} minutos",
            inline=True
        )

        embed.add_field(
            name="📝 Motivo",
            value=motivo,
            inline=False
        )

        embed.set_footer(
            text=f"Aplicado por {interaction.user}"
        )

        await interaction.response.send_message(embed=embed)

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Não tenho permissão para dar timeout nesse membro.",
            ephemeral=True
        )

    except Exception as erro:
        print(f"❌ ERRO NO /TIMEOUT: {erro}")

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Ocorreu um erro ao aplicar o timeout.",
                ephemeral=True
            )
# /lock
@bot.tree.command(name="lock", description="Tranca o canal atual.")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):

    canal = interaction.channel

    overwrite = canal.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = False

    await canal.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        "🔒 **Canal trancado.**"
    )


# /unlock
@bot.tree.command(name="unlock", description="Destranca o canal atual.")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):

    canal = interaction.channel

    overwrite = canal.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = None

    await canal.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        "🔓 **Canal destrancado.**"
    )


# Mensagem para quem tentar usar comando sem permissão
@bot.tree.error
async def erro_comando(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        if interaction.response.is_done():
            await interaction.followup.send(
                "❌ Você não tem permissão para usar esse comando.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Você não tem permissão para usar esse comando.",
                ephemeral=True
            )
# ...todos os códigos acima...

# ==========================================
# 📋 LOGS - OS ORIGINAIS
# ==========================================

# O bot procura o canal "logs" automaticamente.
# Se ele não existir, tenta criar o canal.
CANAL_LOGS = None
NOME_CANAL_LOGS = "logs"


async def preparar_canal_logs():
    global CANAL_LOGS

    for guild in bot.guilds:
        canal = discord.utils.get(guild.text_channels, name=NOME_CANAL_LOGS)

        if canal is None:
            try:
                canais = await guild.fetch_channels()
                canal = discord.utils.find(
                    lambda c: isinstance(c, discord.TextChannel)
                    and c.name == NOME_CANAL_LOGS,
                    canais
                )
            except discord.Forbidden:
                print(f"❌ O bot não consegue visualizar os canais de {guild.name}.")
                continue
            except discord.HTTPException as erro:
                print(f"❌ Erro ao buscar os canais de {guild.name}: {erro}")
                continue

        if canal is None:
            try:
                canal = await guild.create_text_channel(
                    NOME_CANAL_LOGS,
                    reason="Criação automática do canal de logs do bot"
                )
                print(f"✅ Canal #{NOME_CANAL_LOGS} criado no servidor {guild.name}.")
            except discord.Forbidden:
                print(f"❌ Dê ao bot a permissão 'Gerenciar Canais' em {guild.name}.")
                continue
            except discord.HTTPException as erro:
                print(f"❌ Erro ao criar o canal #{NOME_CANAL_LOGS}: {erro}")
                continue

        CANAL_LOGS = canal.id
        print(f"✅ Canal de logs configurado: #{canal.name} ({canal.id})")
        return canal

    print("❌ Não foi possível encontrar o canal #logs em nenhum servidor.")
    return None


def pegar_canal_logs():
    if CANAL_LOGS is None:
        return None
    return bot.get_channel(CANAL_LOGS)


# 🗑️ MENSAGEM APAGADA
@bot.event
async def on_message_delete(message):

    if message.author.bot:
        return

    canal_logs = pegar_canal_logs()

    if canal_logs is None:
        print("❌ Canal de logs não encontrado.")
        return

    conteudo = message.content or "Sem conteúdo de texto."

    # Evita embed gigante
    if len(conteudo) > 1000:
        conteudo = conteudo[:1000] + "..."

    embed = discord.Embed(
        title="🗑️ Mensagem apagada",
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="👤 Autor",
        value=f"{message.author.mention}\n`{message.author.id}`",
        inline=True
    )

    embed.add_field(
        name="📍 Canal",
        value=message.channel.mention,
        inline=True
    )

    embed.add_field(
        name="💬 Mensagem",
        value=conteudo,
        inline=False
    )

    embed.set_thumbnail(
        url=message.author.display_avatar.url
    )

    embed.set_footer(
        text=f"Mensagem ID: {message.id}"
    )

    await canal_logs.send(embed=embed)


# ✏️ MENSAGEM EDITADA
@bot.event
async def on_message_edit(before, after):

    if before.author.bot:
        return

    # Não cria log se o conteúdo não mudou
    if before.content == after.content:
        return

    canal_logs = pegar_canal_logs()

    if canal_logs is None:
        return

    antes = before.content or "Sem conteúdo."
    depois = after.content or "Sem conteúdo."

    if len(antes) > 900:
        antes = antes[:900] + "..."

    if len(depois) > 900:
        depois = depois[:900] + "..."

    embed = discord.Embed(
        title="✏️ Mensagem editada",
        color=discord.Color.orange(),
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="👤 Autor",
        value=f"{before.author.mention}\n`{before.author.id}`",
        inline=True
    )

    embed.add_field(
        name="📍 Canal",
        value=before.channel.mention,
        inline=True
    )

    embed.add_field(
        name="📝 Antes",
        value=antes,
        inline=False
    )

    embed.add_field(
        name="📝 Depois",
        value=depois,
        inline=False
    )

    embed.add_field(
        name="🔗 Ir para mensagem",
        value=f"[Clique aqui]({after.jump_url})",
        inline=False
    )

    embed.set_thumbnail(
        url=before.author.display_avatar.url
    )

    await canal_logs.send(embed=embed)

async def enviar_log_moderacao(
    titulo,
    moderador,
    usuario=None,
    motivo=None,
    detalhes=None
):
    canal = pegar_canal_logs()

    if canal is None:
        canal = await preparar_canal_logs()

    if canal is None:
        print("❌ Canal de logs não encontrado.")
        return

    embed = discord.Embed(
        title=titulo,
        color=discord.Color.purple(),
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="🛡️ Moderador",
        value=f"{moderador.mention}\n`{moderador.id}`",
        inline=True
    )

    if usuario:
        embed.add_field(
            name="👤 Usuário",
            value=f"{usuario.mention}\n`{usuario.id}`",
            inline=True
        )

    if motivo:
        embed.add_field(
            name="📝 Motivo",
            value=motivo,
            inline=False
        )

    if detalhes:
        embed.add_field(
            name="📋 Detalhes",
            value=detalhes,
            inline=False
        )

    embed.set_footer(text="Os Originais • Sistema de Moderação")

    await canal.send(embed=embed)

# ==========================================
# 📢 SISTEMA DE EMBED - OS ORIGINAIS
# ==========================================

@bot.tree.command(
    name="embed",
    description="Envia uma mensagem personalizada em embed."
)
@app_commands.describe(
    titulo="Título do embed",
    mensagem="Texto principal",
    canal="Canal onde o embed será enviado",
    imagem="Link de uma imagem (opcional)",
    rodape="Texto no final do embed (opcional)",
    miniatura="Link de uma miniatura (opcional)",
cor="Cor do embed: roxo, vermelho, azul, verde, preto..."
)
@app_commands.checks.has_permissions(manage_messages=True)
async def criar_embed(
    interaction: discord.Interaction,
    titulo: str,
    mensagem: str,
    canal: discord.TextChannel,
    imagem: str = None,
    rodape: str = "Os Originais",
    miniatura: str = None,
    cor: str = "roxo"):
    cores = {
        "roxo": discord.Color.purple(),
        "vermelho": discord.Color.red(),
        "azul": discord.Color.blue(),
        "verde": discord.Color.green(),
        "amarelo": discord.Color.yellow(),
        "laranja": discord.Color.orange(),
        "preto": discord.Color.from_rgb(0, 0, 0),
        "rosa": discord.Color.from_rgb(255, 105, 180),
        "branco": discord.Color.from_rgb(255, 255, 255)
    }

    cor_embed = cores.get(cor.lower(), discord.Color.purple())

    try:
        embed = discord.Embed(
            title=titulo,
            description=mensagem,
            color=cor_embed,
            timestamp=discord.utils.utcnow()
        )
        # Mostra quem criou
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )

                # Imagem opcional
        if imagem:
            if imagem.startswith(("http://", "https://")):
                embed.set_image(url=imagem)
                # Miniatura opcional
                
        if miniatura:
            if miniatura.startswith(("http://", "https://")):
                embed.set_thumbnail(url=miniatura)
            else:
                await interaction.response.send_message(
                    "❌ O campo miniatura precisa ser um link começando com http:// ou https://",
                    ephemeral=True
                )
                return
        # Rodapé
        if rodape:
            embed.set_footer(text=rodape)

        # Envia
        await canal.send(embed=embed)

        await interaction.response.send_message(
            f"✅ Embed enviado em {canal.mention}!",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Não tenho permissão para enviar mensagens nesse canal.",
            ephemeral=True
        )

    except Exception as erro:
        print(f"❌ ERRO NO /EMBED: {erro}")

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Ocorreu um erro ao criar o embed.",
                ephemeral=True
            )

# ==========================================
# 👤 USERINFO
# ==========================================

@bot.tree.command(
    name="userinfo",
    description="Mostra informações de um membro."
)
@app_commands.describe(
    usuario="Membro que você deseja consultar"
)
async def userinfo(
    interaction: discord.Interaction,
    usuario: discord.Member = None
):
    usuario = usuario or interaction.user

    # Cargos, removendo @everyone
    cargos = [
        cargo.mention
        for cargo in usuario.roles
        if cargo != interaction.guild.default_role
    ]

    cargos.reverse()

    if cargos:
        texto_cargos = " ".join(cargos)

        if len(texto_cargos) > 1000:
            texto_cargos = texto_cargos[:1000] + "..."
    else:
        texto_cargos = "Nenhum cargo."

    embed = discord.Embed(
        title=f"👤 Informações de {usuario.display_name}",
        color=discord.Color.purple(),
        timestamp=discord.utils.utcnow()
    )

    embed.set_thumbnail(
        url=usuario.display_avatar.url
    )

    embed.add_field(
        name="🏷️ Usuário",
        value=usuario.mention,
        inline=True
    )

    embed.add_field(
        name="🆔 ID",
        value=f"`{usuario.id}`",
        inline=True
    )

    embed.add_field(
        name="🤖 É bot?",
        value="Sim" if usuario.bot else "Não",
        inline=True
    )

    embed.add_field(
        name="📅 Conta criada",
        value=discord.utils.format_dt(
            usuario.created_at,
            style="F"
        ),
        inline=False
    )

    if usuario.joined_at:
        embed.add_field(
            name="📥 Entrou no servidor",
            value=discord.utils.format_dt(
                usuario.joined_at,
                style="F"
            ),
            inline=False
        )

    embed.add_field(
        name=f"🎭 Cargos ({len(cargos)})",
        value=texto_cargos,
        inline=False
    )

    embed.set_footer(
        text="Os Originais • User Info"
    )

    await interaction.response.send_message(
        embed=embed
    )


# ==========================================
# 💬 SAY
# ==========================================

@bot.tree.command(
    name="say",
    description="Faz o bot enviar uma mensagem."
)
@app_commands.describe(
    mensagem="Mensagem que será enviada",
    canal="Canal onde a mensagem será enviada"
)
@app_commands.checks.has_permissions(
    manage_messages=True
)
async def say(
    interaction: discord.Interaction,
    mensagem: str,
    canal: discord.TextChannel
):
    try:
        await canal.send(mensagem)

        await interaction.response.send_message(
            f"✅ Mensagem enviada em {canal.mention}.",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Não tenho permissão para enviar mensagens nesse canal.",
            ephemeral=True
        )

    except Exception as erro:
        print(f"❌ ERRO NO /SAY: {erro}")

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Ocorreu um erro ao enviar a mensagem.",
                ephemeral=True
            )

bot.run(TOKEN)