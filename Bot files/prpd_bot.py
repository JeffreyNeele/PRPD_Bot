####################################################################################################
#                                                                                                  #
# Copyright 2020, Jeffrey Neele, All rights reserved                                               #
#                                                                                                  #
####################################################################################################

#https://realpython.com/how-to-make-a-discord-bot-python/ - website with basic tutorial

import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

#Load variables from .env file
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

prefixCommand = 'bot.'

client = commands.Bot(command_prefix=prefixCommand)
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='Coffin meme'))
    print(f'{client.user} is connected')

@client.event
async def on_message(message):

    #Return when author is the bot - prevents infinite recursion
    if message.author == client.user:
        return

    #Send a message in the channel as an answer to certain phrases
    if message.content.lower() == 'jason':
        await message.channel.send('Derulo')

    elif message.content.lower() == 'jeffrey' or message.content.lower() == 'jeff':
        await message.channel.send('My name is Jeff')
        await message.channel.send(file=discord.File('my_name_jeff.jpg'))

    elif message.content.lower() == 'michiel':
        await message.channel.send('de Ruyter')

    elif message.content.lower() == 'jelmer':
        await message.channel.send('Bedoel je niet Jelke?')
        
    elif message.content.lower() == 'victor':
        await message.channel.send('RIP')
    #If no phrase is present, check for commands
    else:
        await client.process_commands(message)

# help: Command
@client.command()
async def help(ctx):

    commandDict = {
        'noPlay A B' : 'Let player \'A\' know not to play \'B\'',
        'neverGiveUp' : 'Let others know you will never give up on them',
        'selectRoles' : 'Randomly assign roles to original 5 people',
        'selectRoles A B C D E' : 'Randomly assign roles to players A B C D E (max 5 players)',
        'sendHugs A' : 'Give another user a hug'
    }

    embedHelp = discord.Embed(
        title = 'Help - PRPD bot',
        description = 'A guide to all the commands',
        colour = discord.Colour.green()
    )

    count = 0

    for i in commandDict.keys():
        nameField = f'{count + 1}' + ': ' + prefixCommand + i
        valueField = commandDict[i]
        embedHelp.add_field(name=nameField, value=valueField, inline=False)
        count += 1

    await ctx.send(embed=embedHelp)

# neverGiveUp: Command to remind people to not give up
@client.command()
async def neverGiveUp(ctx):
    output = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    await ctx.send(output)

# noPlay: Command which tells someone to not play something
@client.command()
async def noPlay(ctx, target, *args):

    notPlay = args[0]

    for i in range(1,len(args),1):
        notPlay += ' ' + args[i]

    output = target + ' stop playing ' + notPlay + ', it\'s not going to happen'
    
    await ctx.send(output)
 
# selectRoles A B C D E: Command which randomly gives League of Legends roles to the users (max 5)
# selectRoles:           Default command
@client.command()
async def selectRoles(ctx, *args):

    roles = ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
    players = []
    if not args:
        players = ['Jason', 'Jeffrey', 'Jelmer', 'Michiel', 'Victor']
        random.shuffle(players)
    elif len(args) > 5:
        await ctx.send('input contains too many players, max 5')
        return
    else:
        for words in args:
            players.append(words)
        random.shuffle(roles)

    output = players[0] + " : " + roles[0]

    for i in range(1,len(players),1):
        output += "\n" + players[i] + " : " + roles[i]

    await ctx.send(output)

# sendHugs: Command to send a hug to someone
@client.command()
async def sendHugs(ctx, *args):
    
    #Retrieve author
    author = ctx.message.author.mention

    #Print output in the proper format
    target = args[0]
    for i in range(1,len(args),1):
        target += ' ' + args[i]

    #Case 1: only bot is mentioned
    #Case 2: when bot + other is mentioned or only others
    #NOTE: when in server/guild, let bot role not have same name as bot self as the target will then change from user to role
    if client.user.mentioned_in(ctx.message) and len(ctx.message.mentions) == 1:
        output = 'Thank you ' + author + ' :sparkling_heart:'
    else:
        output = author + ' gives warm hugs to ' + target

    await ctx.send(output)

client.run(TOKEN)
