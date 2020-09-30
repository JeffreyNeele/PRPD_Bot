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

import json
from riotwatcher import LolWatcher, ApiError        #Makes it possible to retrieve data from riotAPI, methods return dictionaries from JSON files


class RiotObj:

    #Regional information
    region = 'euw1'

    def __init__(self, keyAPI):
        
        #Create lolwatcher, needs riotAPI key as input
        self.lol_watcher = LolWatcher(keyAPI)

    #Method which returns a list of all LoL champions
    def getAllChampions(self):

        champions_version = self.getLatestVersion()
        current_champ_list = self.lol_watcher.data_dragon.champions(champions_version)
        
        return current_champ_list['data']

    #Method which obtains the latest version of LoL
    def getLatestVersion(self):
        versions = self.lol_watcher.data_dragon.versions_for_region(self.region)
        champions_version = versions['n']['champion']
        
        return champions_version
    
    #Method which obtains live match information for a given summoner. Returns a dictionary
    def getLiveMatch(self, id):

        match = self.lol_watcher.spectator.by_summoner(self.region, id)

        return match

    #Method which obtains the server status for LoL EUW server. Returns a dictionary
    def getLolStatus(self):
        
        status = self.lol_watcher.lol_status.shard_data(self.region)['services']
        return status
    
    #Method which converts mapID to map name
    def getMap(self, mapId):

        if mapId == 11:
            return 'Summoner\'s Rift'
        elif mapId == 12:
            return 'Howling Abyss'
        elif mapId == 21:
            return 'Nexus Blitz'
        else:
            return ''
    
    #Method which retrieves all the runesReforged from Riot Games by using riotAPI
    def getAllRunes(self):

        version = self.getLatestVersion()
        runesReforged = self.lol_watcher.data_dragon.runes_reforged(version)
        
        return runesReforged

    #Method which returns the target runeStyle
    def getRuneStyle(self, styleID):

        allRunes = self.getAllRunes()

        for rune in allRunes:
            if rune['id'] == styleID:
                return rune

    #Method which returns the target rune from the target runeStyle
    def getRuneTarget(self, runeID, runeStyle):

        for runeList in runeStyle['slots']:
            for rune in runeList['runes']:
                if rune['id'] == runeID:
                    return rune


    #Method which obtains summoner information from Riot Games by using riotAPI. Returns a dictionary
    def getSummoner(self, name):

        summoner = self.lol_watcher.summoner.by_name(self.region, name)

        return summoner

    #Method obtains all ranked information for a summoner
    def getSummonerRankInfo(self, summonerID):

        rankInfo = self.lol_watcher.league.by_summoner(self.region, summonerID)

        return rankInfo

    #Method obtains all summoner spell information
    def getSummonerSpells(self):

        version = self.getLatestVersion()
        allSummonerSpells = self.lol_watcher.data_dragon.summoner_spells(version)

        return allSummonerSpells['data']

    #Method obtains total mastery points from Riot Games by using riotAPI
    def getTotalChampionMastery(self, summonerID):

        mastery = self.lol_watcher.champion_mastery.scores_by_summoner(self.region, summonerID)
        
        return str(mastery)


