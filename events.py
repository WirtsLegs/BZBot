import discord
import questions
import config
import pytz
import dill


class DCSEvent:

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
        self.reminderSent = False
        self.channel = args['channel']
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

    async def react_handle(self, emoji, message, member, user, bot):
        await message.remove_reaction(emoji, user)
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
            elif full_emote == config.configReact:
                config_role = False
                if userTuple == self.author or any(item.id in config.admin_roles for item in member.roles):
                    config_role = True

                dmChannel = await user.send("\u200b")
                if config_role:
                    reply = await questions.askMultChoice((user, bot, dmChannel.channel), "Please select an option:", None, ['Summary', 'Edit', 'Delete'])
                else:
                    reply = "Summary"

                if reply == "Summary":
                    await user.send(embed=self.generateSummary())
                elif reply == "Edit":
                    await user.send("Editing not implemented yet")
                elif reply == "Delete":
                    reply = await questions.askYesNoQuestion((user, bot, dmChannel.channel),
                                                             "Are you sure you want to delete the above event?",
                                                             "Type 'yes' to confirm")
                    if reply == "Yes":
                        await user.send("Deleting Event")
                        return "DELETE"
                    else:
                        await user.send("such a tease, guess I wont delete it")


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
        emb = self.generateEmbed()
        await message.edit(embed=emb)
        return True

    # generates the embed thhat will be posted to the event channel
    def generatePlayerString(self, players, airframe=True, splitlist=False):
        result = "\u200b"
        result2 = "\u200b"
        pl = players.copy()
        padding = 4-len(pl)
        ten = []
        count1 = 0
        count2 = 0

        if airframe:
            for p in pl:
                if p in self.tentative:
                    ten.append(p)
                else:
                    result = result + p[1] + "\n"
                    count1 = count1+1
            if len(ten) > 0:
                if not splitlist:
                    #if len(pl) > len(ten):
                    #    result = result + "----\n"
                    for p in ten:
                        result = result + "*" + p[1] + "\n"
                        count1 = count1 + 1
                else:
                    for p in ten:
                        result2 = result2 + p[1] + "\n"
                        count2 = count2 + 1
        else:
            for p in pl:
                result = result + p[1] + "\n"
                count1 = count1 + 1
        if not splitlist:
            if padding > 0:
                result = result+("\n\u200b"*padding)
        return result, result2, count1, count2

    def getAccepted(self):
        for k in list(self.player_roles.keys()):
            accepted=[]
            for p in self.player_roles[k]:
                if p not in self.tentative:
                    accepted.append(p)
            return accepted
    def getAcceptedTentativeString(self,tentative=False):
        playerlist = "\u200b"
        count=0
        used=[]
        if not tentative:
            for k in list(self.player_roles.keys()):
                for p in self.player_roles[k]:
                    if p not in self.tentative:
                        if p not in used:
                            count = count + 1
                            playerlist = playerlist + p[1] + "\n"
                        used.append(p)
        else:
            for p in self.tentative:
                count = count+1
                playerlist = playerlist + p[1] + "\n"

        return playerlist, count

    def generateEmbed(self):
        embed = discord.Embed(title=self.title, description=self.description, timestamp=self.timeUTC)
        embed.set_footer(text="Local Time")
        embed.add_field(name="Author", value=self.author[1], inline=False)
        time = str(self.timeUTC.timestamp()).split(".")[0]
        embed.add_field(name="Event Time: "+self.timeUTC.strftime("%b %d, %Y %H:%M:%S ZULU"), value="**Local Time: <t:" + time + ":f>**", inline=False)
        embed.add_field(name="Difficulty", value=str(self.difficulty) + "/10", inline=True)
        embed.add_field(name="Map", value=self.terrain, inline=True)
        embed.add_field(name="ModPack", value=self.modpack, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        for a in self.roles:
            plist = self.generatePlayerString(self.player_roles[a])
            players = plist[0]
            count = plist[2]
            embed.add_field(name=a[1]+" "+a[0]+" ("+str(count)+")", value=players, inline=True)

        embed.add_field(name="\u200b", value="\u200b", inline=False)
        plist = self.generatePlayerString(self.tentative, False)
        players = plist[0]
        count = plist[2]
        embed.add_field(name=config.tentativeReact+" Tentative ("+str(count)+")", value=players, inline=True, )
        plist = self.generatePlayerString(self.declined)
        players = plist[0]
        count = plist[2]
        embed.add_field(name=config.declinedReact+" Grounded ("+str(count)+")", value=players, inline=True)

        return embed

    def generateSummary(self):
        embed = discord.Embed(title=self.title, description="Summary for this event is as follows", timestamp=self.timeUTC)
        embed.add_field(name="Event Time", value=self.timeUTC.strftime("%m/%d/%Y, %H:%M:%S UTC"), inline=False)
        accepted = self.getAcceptedTentativeString()
        embed.add_field(name="Accepted("+str(accepted[1])+")", value=accepted[0], inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        for a in self.roles:
            plist = self.generatePlayerString(self.player_roles[a], splitlist=True)
            players = plist[0]
            count = plist[2]
            if count > 0:
                embed.add_field(name=a[1] + " " + a[0]+" ("+str(count)+")", value=players, inline=True)
        tentative = accepted = self.getAcceptedTentativeString(True)
        embed.add_field(name="Tentative("+str(tentative[1])+")", value=tentative[0], inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        for a in self.roles:
            plist = self.generatePlayerString(self.player_roles[a], splitlist=True)
            players = plist[1]
            count = plist[3]
            if count > 0:
                embed.add_field(name=a[1] + " " + a[0]+" ("+str(count)+")", value=players, inline=True)
        plist = self.generatePlayerString(self.declined)
        players = plist[0]
        count = plist[2]
        embed.add_field(name="Declined ("+str(count)+")", value=players, inline=False)
        embed.set_footer(text="Local Time")
        return embed
