# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from flask import Flask
from threading import Thread

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
        """ Synchroniser les commandes slash avec Discord """
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
@bot.tree.command(name="annonce", description="Créer une annonce dans un salon spécifié.")
@app_commands.describe(channel="Le salon où envoyer l'annonce", message="Le message de l'annonce")
async def annonce(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    """Commande slash pour créer une annonce dans un salon spécifique."""
    # Vérifier les permissions de l'utilisateur
    if not has_authorized_role(interaction):
        await interaction.response.send_message(
            "❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True
        )
        return

    # Créer un embed stylé pour l'annonce
    embed = discord.Embed(
        description=message,
        color=discord.Color.blue()
    )
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
    embed.set_footer(text=f"Annonce par {interaction.user.name}")

    try:
        # Envoyer l'embed dans le salon spécifié
        await channel.send(embed=embed)

        # Répondre à l'utilisateur pour confirmer l'envoi
        await interaction.response.send_message(
            f"✅ L'annonce a été envoyée dans {channel.mention}.", ephemeral=True
        )

    except Exception as e:
        await interaction.response.send_message(
            "⏰ Une erreur est survenue lors de l'envoi de l'annonce. Veuillez réessayer.", ephemeral=True
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
