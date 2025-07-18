import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext import tasks
import random
import asyncio
import os
import logging
from collections import defaultdict
from datetime import datetime, timedelta

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError("DISCORD_TOKEN is not set in the .env file")

# Optional logging setup
logging.basicConfig(level=logging.DEBUG, filename='discord.log', filemode='w', encoding='utf-8')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
valorant_launch_log = defaultdict(list)

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Chat... we are so back. {bot.user.name} is ready to use!")
    #weekly_reminder.start()

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the clerb {member.name} <3")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    #suckyfish picture spam
    if "!sucky" in message.content.lower():
        await message.channel.send(file=discord.File("media/sucky.png"))

    await bot.process_commands(message)

@tasks.loop(hours=168)
async def weekly_reminder():
    channel = bot.get_channel(1394558132839121016)
    await channel.send("🏃‍♂️ Weekly Reminder: Don’t forget to log at least 3 Strava activities this week! 💪 React if you did an exercise today 💯")

@bot.command()
async def jazzy(ctx):
    folder_path = "media/jasper"

    images = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.gif', '.jpeg'))]

    if not images:
        await ctx.send("No images found!")
        return

    chosen_image = random.choice(images)

    await ctx.send(file=discord.File(os.path.join(folder_path, chosen_image)))

@bot.event
async def on_presence_update(before, after):
    if after.bot:
        return

    # Get all activity names before and after
    before_names = {a.name.lower() for a in before.activities if a.name}
    after_names = {a.name.lower() for a in after.activities if a.name}

    # Check if Valorant was just launched
    if "valorant" in after_names and "valorant" not in before_names:
        now = datetime.utcnow()
        valorant_launch_log[after.id].append(now)
        channel = bot.get_channel(1212947659103674370)  # Replace with your actual channel ID
        if channel:
            await channel.send(f"{after.display_name} just launched **VALORANT**! Manifesting a W for u bestie 💫")

@bot.command()
async def val(ctx, member: discord.Member = None):
    member = member or ctx.author  # default to the person who sent the command

    now = datetime.utcnow()
    one_week_ago = now - timedelta(days=7)

    launches = [
        t for t in valorant_launch_log.get(member.id, [])
        if t >= one_week_ago
    ]

    msg = f"🎮 {member.display_name} has launched Valorant **{len(launches)} time(s)** in the past 7 days."

    if len(launches) > 5:
        msg += "\n...Maybe you should touch some grass 🌿"

    await ctx.send(msg)

bot.run(token)