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
import openai

# download the stopwords corpus
nltk.download('stopwords')

# get the stopwords
stopwords = set(nltk.corpus.stopwords.words('english'))

re_triggers = {
    "capy": re.compile(r"capy|capybara|capys|capybaras", re.IGNORECASE),
    "fuck": re.compile(r"fuck|fucking|fucked|fk|fking|fcked|fcking|fuckin|fuckin'|fucker|fuckers", re.IGNORECASE)
}
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
roast_data = []

# load environment variables from .env file
load_dotenv()

# Get tokens and set up API keys
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Create OpenAI client (v1.0+ API)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# logging handler
handler = logging.FileHandler(filename='jester.log', encoding='utf-8', mode='w')


# setting up intents
# intents are like "permissions" for what events the bot can see
intents = discord.Intents.default() 
intents.message_content = True  # needed to read messages
intents.members = True  # needed to see who joins/leaves

# creating the bot instance
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# READY event handler
# this is called when the bot is ready and connected to Discord
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    print('Ready for some chaos? Let\'s put a smile on that face!')
    await bot.change_presence(activity=discord.Game(name='here with the jokes'))
    
    # Get the channel and count words (only after bot is ready)
    channel = bot.get_channel(1415504944269885604) # change channel when needed
    if channel:
        await frequent_words(channel)
    else:
        print("❌ Could not find channel!")
    
    # load jokes from jokes.json
    global jokes
    with open('jokes.json', 'r', encoding='utf-8') as f:
        jokes = json.load(f)
    print(f"Loaded {len(jokes)} jokes")

    # load roast parameters from roast_parameters.json
    global roast_data
    with open('roast_profiles.json', 'r', encoding='utf-8') as f1:
        roast_data = json.load(f1)
    print(f"Loaded {len(roast_data)} roast parameters")

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
async def help(ctx):
    """Show the help menu"""
    await ctx.send("```" + "Commands:\n" + 
    "!help - Show the help menu\n" + 
    "!ping - Check if the bot is responsive\n" + 
    "!joke - Tell a joke\n" + 
    "!dirtyjoke - Tell a dirty joke\n" + 
    "!roast <nickname> - Roast a user\n" +
    "```")

@bot.command()
async def ping(ctx):
    """Pong! Check if the bot is responsive."""
    # 'ctx' is the "context" - contains message, author, channel, guild info
    await ctx.send(f'🏓 Pong! Latency: {round(bot.latency * 1000)}ms') # sends a message to the channel

@bot.command()
async def joke(ctx):
    """Tell a joke"""
    clean_jokes = [joke for joke in jokes if not joke['mature']]
    formatted_joke = random.choice(clean_jokes)['joke']
    await ctx.send(formatted_joke)

@bot.command(name="dirtyjoke")
async def dirty_joke(ctx):
    """Tell a dirty joke"""
    dirty_jokes = [joke for joke in jokes if joke['mature']]
    formatted_joke = random.choice(dirty_jokes)['joke']
    await ctx.send(formatted_joke)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user) # cooldown of 10 seconds per user
async def roast(ctx, *, nickname: str):
    """Roast a user"""
    # convert nickname to lowercase
    nickname = nickname.lower()

    # search for the profile in roast_data
    found_user_id = None
    found_profile = None
    for userID, profile in roast_data.items():
        if nickname in [n.lower() for n in profile["nickname"]]:  
            found_user_id = int(userID)
            found_profile = profile
            break
    
    if not found_profile:
        await ctx.send(f"who the fuck is {nickname}?")
        return
    
    # Get the Discord user object
    user = await bot.fetch_user(found_user_id)
    if not user:
        await ctx.send(f"Found profile for {nickname} but couldn't find the user in Discord.")
        return
    
    # Use found_profile directly
    roastee = found_profile
    
    nick = random.choice(roastee["nickname"]) if roastee.get("nickname") else user.display_name
    
    # Get all items from lists
    fun_facts = roastee.get("fun_facts", [])
    hobbies = roastee.get("hobbies", [])
    roast_styles = roastee.get("roast_style", [])
    extra_note = roastee.get("extra_note", "")

    # Format lists as comma-separated strings for the prompt
    fun_facts_str = ", ".join(fun_facts) if fun_facts else "None"
    hobbies_str = ", ".join(hobbies) if hobbies else "None"
    roast_styles_str = ", ".join(roast_styles) if roast_styles else "None"

    prompt = f"""You are a professional roast master. You are given a profile of a person and you need to roast them.
            You are given the following information:
            - Nickname: {nick}
            - Fun Facts: {fun_facts_str}
            - Hobbies: {hobbies_str}
            - Roast Styles: {roast_styles_str}
            - Extra Note: {extra_note}

            Limit to 1 fun fact or hobby.
            Consider the extra note when roasting.
            DO NOT USE EVERY PIECE OF INFORMATION GIVEN. DO NOT BE TOO SPECIFIC.
            One sentence is enough. 20 WORDS MAXIMUM.
            Make it witty and funny. 
            Profanity is allowed."""

    try:
        if not openai_client:
            await ctx.send("OpenAI API key not configured.")
            return
        
        # Use asyncio.to_thread to run the synchronous API call in a thread
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a professional roast master. You are given a profile of a person and you need to roast them."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        roast = response.choices[0].message.content
        await ctx.send(f"{user.mention} {roast}")
    except Exception as e:
        await ctx.send(f"Sorry, I couldn't generate a roast. Error: {str(e)}")
        logging.error(f"OpenAI API error: {e}")

async def roast_back(ctx, discord_user_id: int):
    """Roast a user back if they roast the bot"""
    # Look up the profile directly by user ID
    user_id_str = str(discord_user_id)
    
    if user_id_str not in roast_data:
        # If user not in roast_data, still roast them but with limited info
        user = await bot.fetch_user(discord_user_id)
        if not user:
            return  # Can't find user, silently fail
        
        # Simple roast without profile data
        prompt = f"""You are a witty Discord bot that just got roasted. The user {user.display_name} said something mean about you. 
        Roast them back in a funny, clever way. Keep it to one sentence. Be sassy but not too harsh."""
    else:
        # User has a profile, use it
        found_profile = roast_data[user_id_str]
        user = await bot.fetch_user(discord_user_id)
        if not user:
            return
        
        roastee = found_profile
        
        nick = random.choice(roastee["nickname"]) if roastee.get("nickname") else user.display_name
        
        # Get all items from lists
        fun_facts = roastee.get("fun_facts", [])
        hobbies = roastee.get("hobbies", [])
        roast_styles = roastee.get("roast_style", [])
        extra_note = roastee.get("extra_note", "")

        # Format lists as comma-separated strings for the prompt
        fun_facts_str = ", ".join(fun_facts) if fun_facts else "None"
        hobbies_str = ", ".join(hobbies) if hobbies else "None"
        roast_styles_str = ", ".join(roast_styles) if roast_styles else "None"

        prompt = f"""You are a witty Discord bot that just got roasted by someone. They said something mean about you, and now you're roasting them back.
        You are given the following information about the person who roasted you:
        - Nickname: {nick}
        - Fun Facts: {fun_facts_str}
        - Hobbies: {hobbies_str}
        - Roast Styles: {roast_styles_str}
        - Extra Note: {extra_note}

        Roast them back in a funny, clever way. Use their profile information to make it personal and witty.
        Choose AT MOST 1 fun fact and 1 hobby to reference.
        One sentence is enough. Be sassy but not too harsh. This is a friendly roast-back."""

    try:
        if not openai_client:
            return  # Silently fail if no API key
        
        # Use asyncio.to_thread to run the synchronous API call in a thread
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a witty Discord bot that roasts users back when they say mean things about you."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        roast = response.choices[0].message.content
        await ctx.send(f"{user.mention} {roast}")
    except Exception as e:
        logging.error(f"OpenAI API error in roast_back: {e}")
        # Silently fail - don't send error message for auto-roasts

@roast.error
async def roast_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):       # cooldown error caught
        await ctx.send(f"dude chill, calm your tatas and go touch some grass")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

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

        if message.author.name == "cupofshaybutter" and re_triggers["capy"].search(content.lower()):                     
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

        # shames stephen for saying bad words
        if message.author.name == "stephen974" and re_triggers["fuck"].search(message.content.lower()):
            await message.reply("https://tenor.com/view/bad-language-avengers-captain-america-maria-hill-ultron-gif-17239339")
            return

        # example inside joke 2 to test (tests for message content only)
        if "debugging" in message.content.lower():
            await message.add_reaction(":bug:")

        # example inside joke 3 to test (responds to a trigger word)
        triggers = ["stinky", "kiss me", "smelly", "love you"]
        if any(word in message.content.lower() for word in triggers):
            await message.channel.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTNuMW9lY3VvOHA2OHA3aGZkNnI3ODd6aGRteXR1dTl6dGE2dXQ3MyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/OuQmhmAAdJFLi/giphy.gif")

        # Check for profanity/roasting
        if re_triggers["fuck"].search(message.content.lower()) or any(word in message.content.lower() for word in ["shut up", "shut", "stupid", "dumb", "bad", "suck", "hate", "clanker", "clanka", "idiot", "moron", "dickhead", "dick", "asshole", "ass", "fuck", "fucking", "fucked", "fk", "fking", "fcked", "fcking", "fuckin", "fuckin'", "fucker", "fuckers"]):
            await roast_back(message.channel, message.author.id)
            return

    except Exception as e:
        logging.error(f"Error processing message: {e}")
    finally:
        # IMPORTANT: allow commands to keep working
        await bot.process_commands(message)

# Run the bot
if TOKEN:
    bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
else:
    print("❌ ERROR: No token found. Check your .env file!")