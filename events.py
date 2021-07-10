import discord
import config
import pytz


class Event:
    author = ""
    description = ""
    timeUTC = ""
    difficulty = 0
    title = ""
    terrain = ""
    airframes = []
    eID = ""
    state = ""
    modpack = ""
    player_roles = {}

    def __init__(self, args):
        self.author = args["author"]
        self.title = args["title"]
        self.description = args["description"]
        self.terrain = args["map_selection"]
        self.difficulty = args["difficulty"]
        self.modpack = args["modpack"]
        self.timeUTC = args["event_time"].astimezone(pytz.utc)

    # will eventually (maybe if i need it) commit event details to a DB
    def commit_event(self, ev):
        return 0

    # generates the embed thhat will be posted to the event channel
    def generateEmbed(self):
        embed = discord.Embed(title=self.title, description=self.description, timestamp=self.timeUTC)
        embed.set_footer(text="Local Time")
        embed.add_field(name="Author", value=self.author, inline=False)
        embed.add_field(name="Event Time", value=self.timeUTC.strftime("%m/%d/%Y, %H:%M:%S UTC"), inline=False)
        embed.add_field(name="Difficulty", value=str(self.difficulty) + "/10", inline=True)
        embed.add_field(name="Map", value=self.terrain, inline=True)
        embed.add_field(name="ModPack", value=self.modpack, inline=True)

        return embed
