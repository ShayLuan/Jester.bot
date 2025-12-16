# jester.py by Shay Luan

# imports
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# setting up intents
# intents are like "permissions" for what events the bot can see
intents = discord.Intents.default() 
intents.message_content = True  # needed to read messages
intents.members = True  # needed to see who joins/leaves

# creating the bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# READY event handler
# this is called when the bot is ready and connected to Discord
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    print('Ready for some chaos? Let\'s put a smile on that face!')
    await bot.change_presence(activity=discord.Game(name='with inside jokes'))

# simple test command
@bot.command()
async def ping(ctx):
    """Pong! Check if the bot is responsive."""
    # 'ctx' is the "context" - contains message, author, channel, guild info
    await ctx.send(f'🏓 Pong! Latency: {round(bot.latency * 1000)}ms') # sends a message to the channel

# inside joke logic goes here
# This function runs EVERY time a message is sent in any channel the bot can see
@bot.event
async def on_message(message):
    # ignore messages from the bot itself
    # avoids infinite loops
    if message.author == bot.user:
        return
    
    # example inside joke 1 to test (tests for user and message content)
    if message.author.name == "cupofshaybutter" and "coffee" in message.content.lower():
        await message.channel.send(f"{message.author.mention} is a coffee addict ☕")

    # example inside joke 2 to test (tests for message content only)
    if "debugging" in message.content.lower():
        await message.add_reaction("🐛")

    # example inside joke 3 to test (responds to a trigger word)
    triggers = ["stinky", "kiss me", "smelly", "love you"]
    if any(word in message.content.lower() for word in triggers):
        await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTNuMW9lY3VvOHA2OHA3aGZkNnI3ODd6aGRteXR1dTl6dGE2dXQ3MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/OuQmhmAAdJFLi/giphy.gif")

    # IMPORTANT: allow commands to keep working
    await bot.process_commands(message)

# Run the bot
# Get the token from the environment variable .env
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ERROR: No token found. Check your .env file!")