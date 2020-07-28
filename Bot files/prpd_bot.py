####################################################################################################
#                                                                                                  #
# Copyright 2020, Jeffrey Neele, All rights reserved                                               #
#                                                                                                  #
####################################################################################################

#Helpful sources:
# 1 - https://realpython.com/how-to-make-a-discord-bot-python/                              - website with basic tutorial
# 2 - https://www.youtube.com/watch?v=5yahh4tR0L0&list=PLW3GfRiBCHOiEkjvQj0uaUB1Q-RckYnj9   - tutorial series on building a discord bot
# 3 - https://towardsdatascience.com/how-to-use-riot-api-with-python-b93be82dbbd6           - short tutorial about riotAPI
# 4 - https://github.com/pseudonym117/Riot-Watcher                                          - riotwatcher github link
# 5 - https://riot-watcher.readthedocs.io/en/latest/                                        - riotwatcher documentation page

#--------------------------------------------------------------------------------------------------#

import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv
from riotAPI import RiotObj

#Load variables from .env file
load_dotenv()

#Get token from .env file. Token is from the bot (see Discord develop)
TOKEN = os.getenv('DISCORD_TOKEN')
key_API = os.getenv('RIOT_KEY')

prefixCommand = 'bot.'

#Create client
client = commands.Bot(command_prefix=prefixCommand)

#Remove command 'help' to be able to implement own 'help' command
client.remove_command('help')

#Create riotAPI object
riot_API = RiotObj(keyAPI=key_API)


#Event called when the discord bot is ready
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='bot.help for guidance'))
    print(f'{client.user} is connected')

#Event for when a user sends a message through a channel
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
        await message.channel.send(file=discord.File('Images/my_name_jeff.jpg'))

    elif message.content.lower() == 'michiel':
        await message.channel.send('de Ruyter')

    elif message.content.lower() == 'jelmer':
        await message.channel.send('Bedoel je niet Jelke?')
        
    elif message.content.lower() == 'victor':
        await message.channel.send('RIP')

    #If no phrase is present, check for commands
    else:
        await client.process_commands(message)

# help: Command which gives an explanation 
@client.command()
async def help(ctx):

    #Dictionary - Key = command call, Value = explanation of command
    commandDict = {
        'lolStatus' : 'Shows the status of the EUW LOL server',
        'lolSummoner A' : 'Show information about summoner A on EUW',
        'noPlay A B' : 'Let player \'A\' know not to play \'B\'',
        'neverGiveUp' : 'Let others know you will never give up on them',
        'selectRoles' : 'Randomly assign roles to original 5 people',
        'selectRoles A B C D E' : 'Randomly assign roles to players A B C D E (max 5 players)',
        'sendHugs A' : 'Give another user a hug',
        'shouldMe A' : 'Almighty bot will tell you if you should do A',
        'shouldOther A B' : 'Almighty bot will tell if user A should do B'
    }

    #Initialize embed, which makes a nice looking window
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

@client.command()
async def lolStatus(ctx):
    status = riot_API.getLolStatus()

    #Initialize embed, which makes a nice looking window
    embedStatus = discord.Embed(
        title = 'Status LoL services',
        colour = discord.Colour.blue()
    )

    for services in status:
        nameField = services['name']
        serviceStatus = services['status']
        embedStatus.add_field(name=nameField, value=serviceStatus, inline=False)

    await ctx.send(embed=embedStatus)

@client.command()
async def lolSummoner(ctx, *args):

    target = args[0]
    for i in range(1,len(args),1):
        target += ' ' + args[i]

    #Retrieve information of summoner
    try:
        summoner = riot_API.getSummoner(target)
    except:
        await ctx.send('Summoner name does not exist. Please try another name')
    else:
        name = summoner['name']

        #Make embed to showcase summoner
        embedSummoner = discord.Embed(
            title = name,
            colour = discord.Colour.red()
        )

        #Add summoner level to the embed
        embedSummoner.add_field(name='Summoner Level', value=str(summoner['summonerLevel']), inline=True)

        #Add champion mastery level
        masteryLevel = riot_API.getTotalChampionMastery(summoner['id'])
        embedSummoner.add_field(name='Champion mastery', value=masteryLevel, inline=True)

        outputRank = 'Unranked'
        rankInfo = riot_API.getSummonerRankInfo(summoner['id'])

        #Add summoner rank - only obtain the rank for 'RANKED_SOLO_5x5'
        for rankInformation in rankInfo:
            if rankInformation['queueType'] == 'RANKED_SOLO_5x5':
                rankTier = rankInformation['tier']
                rankDivision = rankInformation['rank']
                rankPoints = rankInformation['leaguePoints']
                outputRank = rankTier + ' ' + rankDivision + '\n' + str(rankPoints) + ' LP'
        
        embedSummoner.add_field(name='Rank solo', value=outputRank, inline=True)


        #Add if summoner is in-game right now
        try:
            liveMatchInfo = riot_API.getLiveMatch(summoner['id'])
        except:
            embedSummoner.add_field(name='In-game', value='No', inline=True)
        else:
            mode = liveMatchInfo['gameMode']
            mapID = liveMatchInfo['mapId']
            gameMap = riot_API.getMap(mapID)
            gameType = liveMatchInfo['gameType']
            embedSummoner.add_field(name='In-game', value='Yes\n' + mode + ' - ' + gameMap + '\n' + gameType, inline=False)

        

        #Add profile image to the embed
        nameOfFile = str(summoner['profileIconId']) + '.png'
        path = 'dragontail-10.15.1/10.15.1/img/profileicon/' + nameOfFile

        file = discord.File(path, filename=nameOfFile)
        embedSummoner.set_thumbnail(url='attachment://' + nameOfFile)

        await ctx.send(file=file, embed=embedSummoner)

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

@client.command()
async def shouldMe(ctx, *args):

    chance = random.randint(0, 100)
    output = ''

    if chance <= 49:
        output = 'You should not do '
    else:
        output = 'It is save to do '
    
    target = args[0]
    for i in range(1,len(args),1):
        target += ' ' + args[i]
    
    await ctx.send(output + target)

@client.command()
async def shouldOther(ctx, user, *args):

    chance = random.randint(0, 100)
    output = ''

    if chance <= 49:
        output = user + ' should not do '
    else:
        output = 'It is save for ' + user + ' to do '
    
    target = args[0]
    for i in range(1,len(args),1):
        target += ' ' + args[i]
    
    await ctx.send(output + target)



#SECTION FOR TODO CODE!
#--------------------------------------------------------------------------------------------------#

#Command to test new commands before making it an official command
@client.command()
async def comTest(ctx):
    pass

#TODO: Command which shows basic information of a summoner in a match
@client.command()
async def liveMatch(ctx, *args):

    target = args[0]
    for i in range(1,len(args),1):
        target += ' ' + args[i]

    try:
        summoner = riot_API.getSummoner(target)
    except:
        await ctx.send('Summoner name does not exist. Please try again')
    else:
        encryptSummonerID = summoner['id']

        try:
            liveMatchInfo = riot_API.getLiveMatch(encryptSummonerID)
        except:
            await ctx.send(target + ' is not in a game now')
        else:
            print(liveMatchInfo)

    await ctx.send('Command successful')

#--------------------------------------------------------------------------------------------------#

client.run(TOKEN)