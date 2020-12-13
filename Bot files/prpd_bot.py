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
import json
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
from riotAPI import RiotObj

#Load variables from .env file
load_dotenv()

#Get token and key_api from .env file.
#Token is from the bot (see Discord develop), key_api is from riotAPI
TOKEN = os.getenv('DISCORD_TOKEN')
key_API = os.getenv('RIOT_KEY')

prefixCommand = 'bot.'

#Create client
client = commands.Bot(command_prefix=prefixCommand)

#Remove command 'help' to be able to implement own 'help' command
client.remove_command('help')

#Create riotAPI object
riot_API = RiotObj(keyAPI=key_API)

#Variables for bot commands
championInformationPath = Path('dragontail-10.20.1/10.20.1/data/en_GB/champion/')
championTileImagePath = Path('dragontail-10.20.1/10.20.1/img/champion/')
profileiconPath = Path('dragontail-10.20.1/10.20.1/img/profileicon/')
mapIconPath = Path('dragontail-10.20.1/10.20.1/img/map/')
whitespace = '\u200b'


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

    lowerMessage = message.content.lower()

    #Send a message in the channel as an answer to certain phrases
    if lowerMessage == 'jason':
        await message.channel.send('Derulo')

    elif lowerMessage == 'jeffrey' or lowerMessage == 'jeff' or lowerMessage == 'geoff':
        await message.channel.send('My name is Jeff')
        await message.channel.send(file=discord.File('Images/my_name_jeff.jpg'))

    elif lowerMessage == 'michiel':
        await message.channel.send('de Ruyter')

    elif lowerMessage == 'jelmer':
        await message.channel.send('Bedoel je niet Jelke?')
        
    elif lowerMessage == 'victor':
        await message.channel.send('RIP')

    #If no phrase is present, check for commands
    else:
        await client.process_commands(message)

# help: Command which gives an explanation 
@client.command()
async def help(ctx):

    #Dictionary - Key = command call, Value = explanation of command
    commandDict = {
        'liveMatch A' : 'Shows general match information for summoner A on EUW',
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

#Command which shows basic information of a summoner in a match
@client.command()
async def liveMatch(ctx, *args):

    target = args[0]
    for i in range(1,len(args),1):
        target += ' ' + args[i]

    #First see if summoner exists
    try:
        summoner = riot_API.getSummoner(target)
    except:
        await ctx.send('Summoner name does not exist. Please try again')
    else:

        #Get encryptedID of summoner to get liveMatch information
        encryptSummonerID = summoner['id']

        #If summoner exists, get liveMatch info if summoner is in a LoL game
        try:
            #Get information of live match
            liveMatchInfo = riot_API.getLiveMatch(encryptSummonerID)

            #Get information of all champions
            allChampions = riot_API.getAllChampions()

            #Get summonerspells
            allSummonerSpells = riot_API.getSummonerSpells()


        except:
            await ctx.send(target + ' is not in a game now')
        else:

            #Team Blue variables
            teamBlueName = []
            teamBlueChampion = []

            #Team Red variables
            teamRedName = []
            teamRedChampion = []

            #Target summoner extra information
            targetRuneStyles = []
            targetRunes = []
            targetChampion = ''
            targetSummonerSpells = ''

            #Iterate through all participants
            for summoner in liveMatchInfo['participants']:

                #First set general information
                name = summoner['summonerName']

                #Secondly retrieve the champion of the current player
                championID = str(summoner['championId'])
                currentChampion = ''

                for champion in allChampions:
                    if allChampions[champion]['key'] == championID:
                        currentChampion = allChampions[champion]['id']                    
                        break

                #check if current player is target player
                if name == target:
                    #Retrieve champion
                    targetChampion = currentChampion

                    #Retrieve summoner spells
                    spell1 = str(summoner['spell1Id'])
                    spell2 = str(summoner['spell2Id'])

                    for spells in allSummonerSpells:
                        if allSummonerSpells[spells]['key'] == spell1:
                            targetSummonerSpells = allSummonerSpells[spells]['name']
                    
                    for spells in allSummonerSpells:
                        if allSummonerSpells[spells]['key'] == spell2:
                            targetSummonerSpells += '\n' + allSummonerSpells[spells]['name']


                    #Retrieve rune styles
                    targetRuneStyles.append(summoner['perks']['perkStyle'])
                    targetRuneStyles.append(summoner['perks']['perkSubStyle'])

                    #RunesReforged from target Summoner
                    currentRunes = summoner['perks']['perkIds']

                    #Retrieve runes from main style
                    mainStyle = riot_API.getRuneStyle(targetRuneStyles[0])

                    for i in range(0,4,1):
                        matchRuneID = currentRunes[i]
                        targetRunes.append(riot_API.getRuneTarget(matchRuneID, mainStyle))

                    #Retrieve runes from substyle
                    subStyle = riot_API.getRuneStyle(targetRuneStyles[1])

                    for i in range(4,6,1):
                        matchRuneID = currentRunes[i]
                        targetRunes.append(riot_API.getRuneTarget(matchRuneID, subStyle))

                #Finally, add the current player to their team
                if summoner['teamId'] == 100:
                    teamBlueName.append(name)
                    teamBlueChampion.append(currentChampion)
                else:
                    teamRedName.append(name)
                    teamRedChampion.append(currentChampion)

            #Make embed to showcase summoner
            embedMatch = discord.Embed(
                colour = discord.Colour.blurple()
            )

            #List of files to send with message, mostly used for images
            files = []

            
            #Add profile image to the embed
            nameOfFile = 'map' + str(liveMatchInfo['mapId']) + ".png"
            path = mapIconPath / nameOfFile

            #Add match mode
            mode = liveMatchInfo['gameMode']
            embedMatch.add_field(name='Match Type', value=mode, inline=False)

            #Add map as thumbnail
            thumbnailFile = discord.File(path, filename=nameOfFile)
            files.append(thumbnailFile)
            embedMatch.set_thumbnail(url='attachment://' + nameOfFile)

            #Display info Blue Team
            #Summoners
            valueTeamBlue = ''
            for member in teamBlueName:
                valueTeamBlue += member + '\n'
            embedMatch.add_field(name='Team Blue', value=valueTeamBlue, inline=True)

            #Champions
            valueTeamBlue = ''
            for champion in teamBlueChampion:
                valueTeamBlue += champion + '\n'
            embedMatch.add_field(name='Champions', value=valueTeamBlue, inline=True)

            #Add whitespace
            embedMatch.add_field(name=whitespace, value=whitespace, inline=False)

            #Display info Red Team
            #Summoners
            valueTeamRed = ''
            for member in teamRedName:
                valueTeamRed += member + '\n'
            embedMatch.add_field(name='Team Red', value=valueTeamRed, inline=True)

            #Champions
            valueTeamRed = ''
            for champion in teamRedChampion:
                valueTeamRed += champion + '\n'
            embedMatch.add_field(name='Champions', value=valueTeamRed, inline=True)
            
            #Add whitespace
            embedMatch.add_field(name=whitespace, value=whitespace, inline=False)

            #Display information of the target
            #Main Runes
            mainRunes = targetRunes[0]['name']
            for i in range(1,4,1):
                mainRunes += '\n' + targetRunes[i]['name']

            embedMatch.add_field(name='Main: ' + mainStyle['name'], value=mainRunes, inline=True)

            #Sub Runes
            subRunes = targetRunes[4]['name'] + '\n' + targetRunes[5]['name']
            embedMatch.add_field(name='Sub: ' + subStyle['name'], value=subRunes, inline=True)

            #Summoner spells
            embedMatch.add_field(name='Summoner Spells', value=targetSummonerSpells, inline=True)

            #Add current champion picture
            championURL = allChampions[targetChampion]['image']['full']            
            path = championTileImagePath / championURL

            championFile = discord.File(path, filename=championURL)
            files.append(championFile)
            embedMatch.set_author(name=target + ' Match', icon_url='attachment://' + championURL)
            
            await ctx.send(files=files, embed=embedMatch)

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
        nameOfFile = str(summoner['profileIconId']) + ".png"
        path = profileiconPath / nameOfFile

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
    
    allSummonerSpells = riot_API.getAllChampions()
    print(allSummonerSpells['Aatrox'])

#TODO: Command which shows basic information of a summoner in a match
@client.command()
async def champion(ctx, *args):
    
    #Get target name (no spaces, because it is necessary to get the json file)
    target = args[0].capitalize()

    for i in range(1,len(args),1):
        target += args[i].capitalize()   

    try:
        path = championInformationPath / (target + '.json')
        with open(path) as championFile:
            data = json.load(championFile)
            print(data)
    except:
        await ctx.send('Champion name does not exist. Please try again')
    else:
        pass

#--------------------------------------------------------------------------------------------------#

client.run(TOKEN)