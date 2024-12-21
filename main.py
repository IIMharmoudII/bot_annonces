# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from flask import Flask
from threading import Thread
import asyncio

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT_DISCORD')

# Configurer les intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Initialisation du bot
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="&", intents=intents)
        self.synced = False  # Vérifier si les commandes slash sont synchronisées

    async def setup_hook(self):
        # Synchroniser les commandes slash quand le bot est prêt
        if not self.synced:
            await self.tree.sync()
            self.synced = True
            print("Commandes Slash synchronisées avec Discord.")

bot = MyBot()

# === Serveur Web Flask ===
app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne et répond aux pings !"

def run_webserver():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run_webserver)
    thread.start()

# === Liste des rôles autorisés ===
AUTHORIZED_ROLE_IDS = [
    1312420794525024306,  # Rôle 1
    1312420860283322449,  # Rôle 2
    1312422534607667210   # Rôle 3
]

# Vérifier si l'utilisateur a un rôle autorisé
def has_authorized_role(interaction: discord.Interaction):
    """Vérifie si l'utilisateur possède un rôle autorisé."""
    return any(role.id in AUTHORIZED_ROLE_IDS for role in interaction.user.roles)

# === Commande Slash : /annonce ===
@bot.tree.command(name="annonce", description="Créer une annonce stylée.")
async def annonce(interaction: discord.Interaction):
    """Commande slash pour créer une annonce stylée."""
    # Vérifier les permissions de l'utilisateur
    if not has_authorized_role(interaction):
        await interaction.response.send_message(
            "❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True
        )
        return

    # Demander à l'utilisateur d'entrer son annonce
    await interaction.response.send_message(
        "✏️ Veuillez entrer votre annonce dans ce chat (répondez ici). Vous avez 5 minutes.", ephemeral=True
    )

    def check(message):
        return message.author == interaction.user and message.channel == interaction.channel

    try:
        # Attendre le message de l'utilisateur
        message = await bot.wait_for("message", check=check, timeout=300.0)

        # Créer un embed stylé pour l'annonce
        embed = discord.Embed(
            description=message.content,
            color=discord.Color.blue()
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.set_footer(text=f"Annonce par {interaction.user.name}")

        # Envoyer l'embed dans le même salon
        await interaction.channel.send(embed=embed)
        
        # Supprimer le message original de l'utilisateur pour garder le chat propre
        await message.delete()

    except asyncio.TimeoutError:
        await interaction.followup.send(
            "⏰ Le temps imparti est écoulé, vous n'avez pas fourni d'annonce à temps.", ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(
            "⏰ Temps écoulé ou erreur, veuillez réessayer.", ephemeral=True
        )
        print(e)

# === Lancer le serveur Flask et le bot ===
@bot.event
async def on_ready():
    """Événement lancé lorsque le bot est prêt."""
    print(f"Bot connecté en tant que {bot.user}")
    try:
        # Synchroniser les commandes slash quand le bot est prêt
        await bot.tree.sync()
        print("Commandes Slash synchronisées.")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes slash : {e}")

# === Lancer le serveur Flask et le bot ===
keep_alive()
bot.run(TOKEN)
