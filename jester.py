# jester.py by Shay Luan

# imports
import collections
import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import re # regex for pattern matching
import random
import asyncio
import nltk
import json

# download the stopwords corpus
nltk.download('stopwords')

# get the stopwords
stopwords = set(nltk.corpus.stopwords.words('english'))

re_triggers = [
    re.compile(r"\bcapy|capybara|capys|capybaras\b", re.IGNORECASE)
]
capy_responses = [
    "Remember, capybaras are not life, you still have Mareighanne 💖",
    "Remember, capybaras are not real, they're a construct of capitalism",
    "Idk man, wombats are just better ngl",
    "yeah yeah go ahead and marry a capybara, why don't ya",
    "aren't capybaras just giant rats",
    "bro forget about capys, go touch some grass",
    "you know who's touching more grass than you? Capybaras"
]

# module level variables
jokes = []

# load environment variables from .env file
load_dotenv()

# logging handler
handler = logging.FileHandler(filename='jester.log', encoding='utf-8', mode='w')


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
    await bot.change_presence(activity=discord.Game(name='here with the jokes'))
    
    # Get the channel and count words (only after bot is ready)
    channel = bot.get_channel(1415504944269885604)
    if channel:
        await frequent_words(channel)
    else:
        print("❌ Could not find channel!")
    
    # load jokes from jokes.json
    global jokes
    with open('jokes.json', 'r', encoding='utf-8') as f:
        jokes = json.load(f)
    print(f"Loaded {len(jokes)} jokes")


# counting most used words for a user
async def frequent_words(channel):
    user_word_counts = collections.defaultdict(collections.Counter)
    
    # Convert stopwords to lowercase for case-insensitive comparison
    stopwords_lower = {word.lower() for word in stopwords}

    async for message in channel.history(limit=3000):
        if message.author == bot.user:
            continue
        
        username = str(message.author)
        words = message.content.split()
        # Convert to lowercase and filter out stopwords and non-alphabetic words
        filtered_words = [word.lower() for word in words if word.lower() not in stopwords_lower and word.isalpha()]
        user_word_counts[username].update(filtered_words)

    # Only keep the top 10 most common words per user
    user_top10_words = {}
    for username, counter in user_word_counts.items():
        user_top10_words[username] = counter.most_common(10)

    # Store top words in dict variables and print formatted output
    for username, top_words in user_top10_words.items():
        # Create a variable name for this user's topwords dictionary
        var_name = f"{username.replace(' ', '_').replace('#', '_').replace('-', '_')}_topwords"
        # Build the dictionary of top words
        topwords_dict = {word: count for word, count in top_words}
        # Assign to globals() so it's available by variable name
        globals()[var_name] = topwords_dict
        print(f"\n{username}:")
        for word, count in top_words:
            print(f"  {word}: {count}")
    
    return user_top10_words

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
    try:
        # ignore messages from the bot itself
        # avoids infinite loops
        if message.author == bot.user:
            return
        
        content = message.content

        if message.author.name == "cupofshaybutter":                    
            for pattern in re_triggers:
                if pattern.search(content):
                    await message.reply(random.choice(capy_responses))
                    return

        # check if the bot is mentioned
        if bot.user in message.mentions:
            content = message.content.lower()

            # respond to "tell me a joke" and "cheer me up"
            if re.search(r"tell me a joke", content) or re.search(r"cheer me up", content):
                clean_jokes = [joke for joke in jokes if not joke['mature']]
                formatted_joke = random.choice(clean_jokes)['joke']
                await message.reply(formatted_joke)
                return

            # respond to "tell me a dirty joke"
            if re.search(r"tell me a dirty joke", content):
                dirty_jokes = [joke for joke in jokes if joke['mature']]
                formatted_joke = random.choice(dirty_jokes)['joke']
                await message.reply(formatted_joke)
                return

        # example inside joke 1 to test (tests for user and message content)
        if message.author.name == "cupofshaybutter" and "coffee" in message.content.lower():
            await message.channel.send(f"{message.author.mention} is a coffee addict ☕")

        # example inside joke 2 to test (tests for message content only)
        if "debugging" in message.content.lower():
            await message.add_reaction(":bug:")

        # example inside joke 3 to test (responds to a trigger word)
        triggers = ["stinky", "kiss me", "smelly", "love you"]
        if any(word in message.content.lower() for word in triggers):
            await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTNuMW9lY3VvOHA2OHA3aGZkNnI3ODd6aGRteXR1dTl6dGE2dXQ3MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/OuQmhmAAdJFLi/giphy.gif")

    except Exception as e:
        logging.error(f"Error processing message: {e}")
    finally:
        # IMPORTANT: allow commands to keep working
        await bot.process_commands(message)

# Run the bot
# Get the token from the environment variable .env
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
else:
    print("❌ ERROR: No token found. Check your .env file!")