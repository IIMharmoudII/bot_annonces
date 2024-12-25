# -*- coding: utf-8 -*-

import discord
from discord.ext import commands  # Importer la classe commands
from flask import Flask
from threading import Thread
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT_DISCORD')  # Assure-toi que le TOKEN est dans ton fichier .env

# Configurer les intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

# Initialisation du bot avec commands.Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# === Smash or Pass ===
TARGET_CHANNEL_ID = 1312570416665071797
VALID_REACTIONS = ["👍", "👎"]
message_threads = {}

# === Serveur Web (Flask) ===
app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === Gestion des événements du bot ===

@bot.event
async def on_ready():
    print(f"Bot Smash or Pass connecté en tant que {bot.user}")

@bot.event
async def on_message(message):
    """Gestion des messages pour le Smash or Pass."""
    if message.author.bot:
        return

    if message.channel.id == TARGET_CHANNEL_ID:
        if not message.attachments:
            await message.delete()
            return

        for reaction in VALID_REACTIONS:
            await message.add_reaction(reaction)

        thread_name = f"Fil de {message.author.display_name}"
        thread = await message.create_thread(name=thread_name)
        message_threads[message.id] = thread.id

        await thread.send(
            f"Bienvenue dans le fil de discussion pour l'image postée par {message.author.mention}.\n"
            f"Merci de respecter la personne et de rester courtois. Tout propos méprisant, dévalorisant, insultant ou méchant est interdit et sera sanctionné !"
        )

    await bot.process_commands(message)  # Processus des commandes ajouté ici

# === Commandes du bot ===
@bot.command()
async def ping(ctx):
    """Commande simple pour tester le bot."""
    await ctx.send("Pong!")

# === Lancer le bot ===
keep_alive()
bot.run(TOKEN)
