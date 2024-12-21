# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT_DISCORD')

# Configurer les intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Initialisation du bot avec le préfixe '&'
bot = commands.Bot(command_prefix="&", intents=intents)

# === Serveur Web Flask ===
app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne et répond aux pings !"

# Fonction pour lancer le serveur Flask dans un thread séparé
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
def has_authorized_role(ctx):
    """Vérifie si l'utilisateur possède un rôle autorisé."""
    return any(role.id in AUTHORIZED_ROLE_IDS for role in ctx.author.roles)

@bot.command()
@commands.check(has_authorized_role)
async def annonce(ctx):
    """Commande pour envoyer une annonce stylée."""
    # Supprime immédiatement la commande pour éviter qu'elle apparaisse dans le chat
    await ctx.message.delete()
    
    # Envoyer un message demandant à l'utilisateur de copier/coller son annonce
    prompt = await ctx.send(f"✏️ {ctx.author.mention}, veuillez copier/coller ou écrire votre annonce ici. Tapez `cancel` pour annuler.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        # Attendre que l'utilisateur entre son annonce
        message = await bot.wait_for("message", check=check, timeout=300.0)
        
        # Vérifier si l'utilisateur a annulé l'annonce
        if message.content.lower() == "cancel":
            await ctx.send("❌ L'annonce a été annulée.", delete_after=10)
            await message.delete()
            return
        
        # Créer un embed stylé pour l'annonce
        embed = discord.Embed(
            description=message.content,
            color=discord.Color.blue()
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text=f"Annonce par {ctx.author.name}")

        # Envoyer l'embed dans le canal
        await ctx.send(embed=embed)

        # Supprimer l'annonce d'origine pour garder le chat propre
        await message.delete()
    except Exception as e:
        await ctx.send("⏰ Temps écoulé ou erreur, veuillez réessayer.", delete_after=10)
        print(e)
    finally:
        # Supprimer le message de prompt initial
        await prompt.delete()

@bot.event
async def on_command_error(ctx, error):
    """Gestion des erreurs de commande."""
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.", delete_after=10)
    else:
        print(error)

# === Lancer le serveur Flask et le bot ===
keep_alive()
bot.run(TOKEN)
