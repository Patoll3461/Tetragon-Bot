import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import asyncio
from time import *
import subprocess
#from config import TOKEN

bot = commands.Bot(command_prefix = "!", intents = discord.Intents.all())
log_channel_id = 1204434514202329100  # Variable to store the log channel ID
linux_channel_id = 1211978296221376532
online = False
players = []

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    with open("users.txt", "r") as file:
        indexi = 0
        for line in file.readlines():
            split = line.split(":")
            name = int(split[0])
            score = int(split[1])
            print(name)
            y = player(int(name), score, indexi)
            players.append(y)
            indexi += 1
    check_logs.start()

@bot.tree.command(name="credits")
@app_commands.choices(option=[
    app_commands.Choice(name="Add", value="Add"),
    app_commands.Choice(name="Remove", value="Remove"),
    app_commands.Choice(name="Set", value="Set"),
    app_commands.Choice(name="Show", value="Show")
]
)
async def credits(ctx: discord.Interaction, option: app_commands.Choice[str], user: discord.User, value: int = 0):
    if (ctx.user.guild_permissions.administrator):
        for x in players:
            print(x.name)
            print(user.id)
            if (x.name == user.id):
                if (option.value == "Add"):
                    x.credits += int(value)
                elif (option.value == "Remove"):
                    x.credits -= int(value)
                elif (option.value == "Show"):
                    await ctx.response.send_message("User has the social credit score of " + str(x.credits) + ".")
                    return
                elif (option.value == "Set"):
                    x.credits = int(value)
                else:
                    await ctx.response.send_message("Please give a valid option!")
                with open("users.txt", "r") as file:
                    lines = file.readlines()
                    lines[x.line] = str(x.name) + ":" + str(x.credits) + "\n"
                    print("hi")
                with open("users.txt", "w") as file:
                    file.write("".join(lines))
                await ctx.response.send_message("Added/removed/set social credit.")
                return
        if (option.value == "Add"):
            y = player(user.id, value, len(players))
            players.append(y)
            await ctx.response.send_message("Created new user and applied value!")
            with open("users.txt", "r") as file:
                lines = file.read()
                print(len(players))
                if (len(players) > 1):
                    lines = lines + "\n" + str(y.name) + ":" + str(y.credits)
                else:
                    lines = str(y.name) + ":" + str(y.credits)
            with open("users.txt", "w") as file:
                file.write("".join(lines))
        elif (option.value == "Remove"):
            y = player(user.id, -value, len(players))
            players.append(y)
            with open("users.txt", "r") as file:
                lines = file.read()
                if (len(players) > 1):
                    lines = lines + "\n" + str(y.name) + ":" + str(y.credits)
                else:
                    lines = str(y.name) + ":" + str(y.credits)
            with open("users.txt", "w") as file:
                file.write("".join(lines))
            await ctx.response.send_message("Created new user and applied value!")
        elif (option.value == "Show"):
            y = player(user.id, 0, len(players))
            players.append(y)
            with open("users.txt", "r") as file:
                lines = file.read()
                if (len(players) > 1):
                    lines = lines + "\n" + str(y.name) + ":" + str(y.credits)
                else:
                    lines = str(y.name) + ":" + str(y.credits)
            with open("users.txt", "w") as file:
                file.write("".join(lines))
            await ctx.response.send_message("User has the social credit score of 0.")
        elif (option.value == "Set"):
            y = player(user.id, value, len(players))
            players.append(y)
            with open("users.txt", "r") as file:
                lines = file.read()
                if (len(players) > 1):
                    lines = lines + "\n" + str(y.name) + ":" + str(y.credits)
                else:
                    lines = str(y.name) + ":" + str(y.credits)
            with open("users.txt", "w") as file:
                file.write("".join(lines))
            await ctx.response.send_message("Set social credit score.")
        else:
            await ctx.response.send_message("Please give a valid option!")
    else:
        await ctx.response.send_message("You dont meet the repuired permissions!", ephemeral=True)

@bot.tree.command(name="socialcredit")
async def socialcredit(ctx: discord.Interaction):
    for x in players:
        if (x.name == ctx.user.id):
            await ctx.response.send_message("Your social credit score is " + str(x.credits) + ".", ephemeral=True)
            return
    y = player(ctx.user.name, 0)
    players.append(y)
    await ctx.response.send_message("Your social credit score is 0.", ephemeral=True)

@bot.tree.command(name="add")
async def add_whitelist(ctx: discord.Interaction, name: str):
    #await ctx.message.add_reaction('<:peepo:1055488069312184320>')
    command = f'screen -S "minecraft" -p 0 -X stuff "whitelist add {name}\n"'
    os.system(command)
    await ctx.response.send_message(f'Added {name} to the whitelist.')

@bot.tree.command(name='cmd')
@commands.has_permissions(administrator=True)
async def cmd(ctx, command: str):
    global online
    if (ctx.user.guild_permissions.administrator):
        commande = f'screen -S "minecraft" -p 0 -X stuff "{command}\n"'
        os.system(commande)
        if command == 'stop':
            online = False
        await ctx.response.send_message(f"Executed command {command}")
    else:
        await ctx.response.send_message("You dont have the required permissions!")
    #await ctx.message.add_reaction('💅')
     
@bot.tree.command(name='setlogchannel')
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx):
    global log_channel_id
    if (ctx.user.guild_permissions.administrator):
        log_channel_id = ctx.channel.id
        await ctx.response.send_message(f'Log channel set to {ctx.channel.mention}')
    else:
        await ctx.response.send_message("You dont have the required permissions!", ephemeral=True)

@bot.tree.command(name='start')
@commands.has_permissions(administrator=True)
async def start(ctx):
    global online
    if (ctx.user.guild_permissions.administrator):
        if online:
            return
        os.system(f"/bin/bash /home/minecraft/server/start2.sh")
        online = True
        await ctx.response.send_message("Starting Server...")
    else:
        await ctx.response.send_message("You dont have the required permisions!", ephemeral=True)

@bot.tree.command(name='setonline')
@commands.has_permissions(administrator=True)
async def set_online(ctx, status: str):
    global online
    if (ctx.user.guild_permissions.administrator):
        if status == 'on':
            online = True
            await ctx.response.send_message("Set status to on")
        elif status == 'off':
            online = False
            await ctx.response.send_message("Set status to off")
        else:
            await ctx.response.send_message('Please give a valid option on/off!')
    else:
        await ctx.response.send_message("You dont have the required permissions", ephemeral=True)

@bot.event
async def on_message(message: str):
    # Check if the message is from a bot to avoid reacting to bot messages
    if message.author.bot:
        return
  
    '''
    # List of keywords to check for
    keywords = ['titus']
    keywords2 = ['minecraft']
    keywords3 = ['ok', 'okay', 'oke', 'oki', 'okey']

    # Check if any keyword is present in the message content
    if any(keyword in message.content.lower() for keyword in keywords):
        # Add a reaction to the message
        await message.add_reaction('<:titus:1169934880822530078>')

    if any(keyword in message.content.lower() for keyword in keywords2):
        # Add a reaction to the message
        await message.add_reaction('<:pepo_minecraft:1110915957200797768>')

    if any(keyword in message.content.lower() for keyword in keywords3):
        # Add a reaction to the message
        await message.add_reaction('<:peepo:1055488069312184320>')
    await bot.process_commands(message)
    '''

@tasks.loop(seconds=1)
async def check_logs():
    global log_channel_id
    if log_channel_id is None:
        return  # Log channel not set, do nothing

    try:
        with open('logs/latest.log', 'r') as log_file:
            current_lines = log_file.readlines()

        # If there are new lines since the last check, send them to the log channel
        if hasattr(check_logs, 'last_lines'):
            new_lines = current_lines[len(check_logs.last_lines):]
            if new_lines:
                log_channel = bot.get_channel(log_channel_id)
                for line in new_lines:
                    await log_channel.send(line.strip())

        check_logs.last_lines = current_lines

    except FileNotFoundError:
        print('latest.log not found. Make sure to provide the correct path.')

@check_logs.before_loop
async def before_check_logs():
    await bot.wait_until_ready()

class player:
    def __init__(self, name: int, creditsi: int, line: int):
        self.name = name
        self.credits = creditsi
        self.line = line

    def print_name(self):
        print(self.name)

bot.run('')

