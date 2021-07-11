import discord
import config
import pytz
import dill


class DCSEvent:
    author = ""
    description = ""
    timeUTC = ""
    difficulty = 0
    title = ""
    terrain = ""
    roles = []
    eID = ""
    state = ""
    modpack = ""
    declined = []
    tentative = []
    player_roles = {}

    def __init__(self, args):
        self.author = args["author"]
        self.title = args["title"]
        self.description = args["description"]
        self.terrain = args["map_selection"]
        self.difficulty = args["difficulty"]
        self.modpack = args["modpack"]
        self.roles = []
        self.declined = []
        self.tentative = []
        self.eID = 0
        for r in args['airframes']:
            self.roles.append((r, config.airframes[r]))
        self.player_roles = {}
        for a in self.roles:
            self.player_roles[a] = []

        self.timeUTC = args["event_time"].astimezone(pytz.utc)


    def write_event(self):
        with open(self.eID+".pkl", 'wb') as outf:
            dill.dump(self, outf, protocol=0)
        print(self.player_roles)
        return

    async def react_handle(self, emoji, message, user, bot):
        full_emote = "<:"+emoji.name+":"+str(emoji.id)+">"
        userTuple = (user.id, user.display_name)
        if full_emote not in [x[1] for x in self.roles]:
            if full_emote == config.declinedReact:
                if userTuple in self.declined:
                    self.declined.remove(userTuple)
                else:
                    self.declined.append(userTuple)
                for r in list(self.player_roles.keys()):
                    try:
                        self.player_roles[r].remove(userTuple)
                    except ValueError:
                        continue
                try:
                    self.tentative.remove(userTuple)
                except ValueError:
                    pass
            elif full_emote == config.tentativeReact:
                if userTuple in self.tentative:
                    self.tentative.remove(userTuple)
                else:
                    self.tentative.append(userTuple)
                try:
                    self.declined.remove(userTuple)
                except ValueError:
                    pass
            elif full_emote == config.deleteReact:
                dmChannel = await user.send("Are you sure you want to delete the event? (yes/no) NOT IMPLEMENTED YET")
            elif full_emote == config.editReact:
                dmChannel = await user.send("Are you sure you want to edit the event? (yes/no) NOT IMPLEMENTED YET")
            else:
                await message.remove_reaction(emoji, user)
                return False
        else:
            try:
                self.declined.remove(userTuple)
            except ValueError:
                pass
            for r in list(self.player_roles.keys()):
                if r[1] == full_emote:
                    if userTuple in self.player_roles[r]:
                        self.player_roles[r].remove(userTuple)
                    else:
                        self.player_roles[r].append(userTuple)
                    print(self.player_roles[r])
        emb = self.generateEmbed()
        await message.edit(embed=emb)
        await message.remove_reaction(emoji, user)
        return True

    # generates the embed thhat will be posted to the event channel
    def generatePlayerString(self,players):
        result = "\u200b"
        padding = 4-len(players)
        for p in players:
            result = result+p[1]+"\n"
        if padding > 0:
            result = result+("\n\u200b"*padding)
        return result

    def generateEmbed(self):
        embed = discord.Embed(title=self.title, description=self.description, timestamp=self.timeUTC)
        embed.set_footer(text="Local Time")
        embed.add_field(name="Author", value=self.author[1], inline=False)
        embed.add_field(name="Event Time", value=self.timeUTC.strftime("%m/%d/%Y, %H:%M:%S UTC"), inline=False)
        embed.add_field(name="Difficulty", value=str(self.difficulty) + "/10", inline=True)
        embed.add_field(name="Map", value=self.terrain, inline=True)
        embed.add_field(name="ModPack", value=self.modpack, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        for a in self.roles:
            players = self.generatePlayerString(self.player_roles[a])
            embed.add_field(name=a[1]+" "+a[0], value=players, inline=True)

        embed.add_field(name="\u200b", value="\u200b", inline=False)
        players = self.generatePlayerString(self.tentative)
        embed.add_field(name=config.tentativeReact+" Tentative", value=players, inline=True, )
        players = self.generatePlayerString(self.declined)
        embed.add_field(name=config.declinedReact+" Grounded", value=players, inline=True)

        return embed
