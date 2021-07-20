import discord

import events
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
        self.updateUsers = []
        self.eID = 0
        self.reminderSent = False
        self.channel = args['channel']
        for r in args['roles']:
            self.roles.append((r, config.airframes[r]))
        self.player_roles = {}
        for a in self.roles:
            self.player_roles[a] = []

        self.timeUTC = args["event_time"].astimezone(pytz.utc)

    async def send_message(self, bot, title, message, accepted=True, tentative=False, footer=None, manualList=[]):
        emb = discord.Embed(title=title, description=message)
        if footer:
            emb.add_field(name="\u200b", value=footer)
        if accepted:
            for p in self.get_accepted():
                user = bot.get_user(p[0])
                await user.send(embed=emb)
        if tentative:
            for p in self.tentative:
                user = bot.get_user(p[0])
                await user.send(embed=emb)
        if len(manualList)>0:
            for p in manualList:
                user = bot.get_user(p[0])
                await user.send(embed=emb)

    def write_event(self):
        with open(str(self.eID)+".pkl", 'wb') as outf:
            dill.dump(self, outf, protocol=0)
        return

    def read_event(self):
        event = None
        with open(str(self.eID)+".pkl", 'wb') as inf:
            event = dill.read(self, inf, protocol=0)
        return event

    async def edit_dialogue(self, bot, channel, user):
        elements = ['title', 'description', 'event_time', 'difficulty', 'map_selection', 'modpack', 'roles']
        info = (user, bot, channel.channel)
        target = await questions.ask_edit(info, "Please select a field to edit", self.generate_edit_embed(),
                                 elements, timeout=60)
        q = None
        for ql in config.question_list:
            if ql[0] == target:
                q = ql
                print(q)
                break
        if q is None:
            return
        reply = ""
        if q[4] == 0:
            reply = await questions.askQuestion(info, q[1], q[2], timeout=q[3])
        elif q[4] == 1:
            reply = await questions.askMultChoice(info, q[1], q[2], q[5], timeout=q[3])
        elif q[4] == 2:
            reply = await questions.askYesNoQuestion(info, q[1], q[2], timeout=q[3])
        elif q[4] == 3:
            reply = await questions.askDateTimeQuestion(info, q[1], q[2], timeout=q[3])
        elif q[4] == 4:
            print(q[5])
            ro = [role[0] for role in self.roles]
            reply = await questions.gatherRoles(info, q[1], q[2], q[5], timeout=q[3], roles=ro)
            print(reply)
        if not reply:
            emb = discord.Embed(title="Right, well fuck you too!")
            await user.send(embed=emb)
            return
        if q[0] == "title":
            self.title = reply
        elif q[0] == "description":
            self.description = reply
        elif q[0] == "event_time":
            self.timeUTC = reply
            self.reminderSent = False
        elif q[0] == "difficulty":
            self.difficulty = reply
        elif q[0] == "map_selection":
            self.terrain = reply
        elif q[0] == "modpack":
            self.modpack = reply
        elif q[0] == "roles":
            self.roles = []
            for r in reply:
                self.roles.append((r, config.airframes[r]))
            print(reply)
            for r in self.roles:
                if r not in list(self.player_roles.keys()):
                    self.player_roles[r] = []
            for pr in list(self.player_roles.keys()):
                if pr not in self.roles:
                    for p in self.player_roles[pr]:
                        if p not in self.updateUsers:
                            self.updateUsers.append(p)
                    self.player_roles.pop(pr)

        reply = await questions.askYesNoQuestion(info, "Would you like to edit anything else?", "yes or no", timeout=60)
        if reply == "Yes":
            await self.edit_dialogue(bot, channel, user)
        else:
            await user.send(embed=self.generate_embed())
            reply = await questions.askYesNoQuestion(info, "Please confirm the above event is as intended", "yes or no",
                                                     timeout=120)
            if reply == "Yes":
                self.write_event()

                reply = await questions.askYesNoQuestion(info, "Would you like to send a update message to participants","yes or no",
                                                         timeout=120)
                if reply == "Yes":
                    chan = bot.get_channel(self.channel)
                    msg = await chan.fetch_message(self.eID)
                    url = msg.jump_url
                    await self.send_message(bot, "A Mission has been Updated: "+self.title, "A mission you are signed up for has been updated\nplease check it to confirm attendance and role selection.\nYou can find the mission signup [here]("+url+")", accepted=True, tentative=True, manualList=self.updateUsers)
                    self.updateUsers = []
                    return True
                else:
                    return True

            else:
                recovery = self.read_event()
                self.author = recovery.author
                self.title = recovery.title
                self.description = recovery.description
                self.terrain = recovery.terrain
                self.difficulty = recovery.difficulty
                self.modpack = recovery.modpack
                self.roles = recovery.roles
                self.declined = recovery.declined
                self.tentative = recovery.tentative
                self.eID = recovery.eID
                self.reminderSent = recovery.reminderSent
                self.channel = recovery.channel
                return False

        return False

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
                    reply = await questions.askMultChoice((user, bot, dmChannel.channel), "Please select an option:", None, ['Summary', 'PM People', 'Edit', 'Delete'], timeout=60)
                else:
                    reply = "Summary"

                if reply == "Summary":
                    await user.send(embed=self.generate_summary())
                elif reply == "Edit":
                    emb = discord.Embed(title="Beginning Editing Process...")
                    await user.send(embed=emb)
                    editres = await self.edit_dialogue(bot, dmChannel, user)
                    emb = discord.Embed(title="Editing Complete!")
                    await user.send(embed=emb)
                    if editres:
                        await message.clear_reactions()
                        emb = self.generate_embed()
                        await message.edit(embed=emb)
                        for a in self.roles:
                            await message.add_reaction(a[1])
                        await message.add_reaction(config.tentativeReact)
                        await message.add_reaction(config.declinedReact)
                        await message.add_reaction(config.configReact)
                elif reply == "PM People":

                    target = await questions.askMultChoice((user, bot, dmChannel.channel), "Who would you like to PM:",
                                                          None, ['All', 'Accepted', 'Tentative'], timeout=60)
                    content = await questions.askQuestion((user, bot, dmChannel.channel), "What is your message?",
                                                          None, timeout=300)
                    if content == None:
                        return
                    chan = bot.get_channel(self.channel)
                    msg = await chan.fetch_message(self.eID)
                    url = msg.jump_url
                    if target == "All":
                        await self.send_message(bot, "Message related to: " + self.title, content,
                                          accepted=True, tentative=True, footer="Link: " + "[" + self.title + "](" + url + ")")
                    elif target == "Accepted":
                        await self.send_message(bot, "Message related to: " + self.title, content,
                                          accepted=True, tentative=False, footer="Link: " + "[" + self.title + "](" + url + ")")
                    elif target == "Tentative":
                        await self.send_message(bot, "Message related to: " + self.title, content,
                                          accepted=False, tentative=True, footer="Link: " + "[" + self.title + "](" + url + ")")

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
        emb = self.generate_embed()
        await message.edit(embed=emb)
        return True

    def generate_player_string(self, players, airframe=True, split_list=False):
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
                if not split_list:
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
        if not split_list:
            if padding > 0:
                result = result+("\n\u200b"*padding)
        return result, result2, count1, count2

    def get_accepted(self):
        accepted = []
        for k in list(self.player_roles.keys()):
            for p in self.player_roles[k]:
                if p not in self.tentative:
                    accepted.append(p)
        return accepted

    def get_accepted_tentative_string(self, tentative=False):
        player_list = "\u200b"
        count = 0
        used = []
        if not tentative:
            for k in list(self.player_roles.keys()):
                for p in self.player_roles[k]:
                    if p not in self.tentative:
                        if p not in used:
                            count = count + 1
                            player_list = player_list + p[1] + "\n"
                        used.append(p)
        else:
            for p in self.tentative:
                count = count+1
                player_list = player_list + p[1] + "\n"

        return player_list, count

    def generate_embed(self):
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
            plist = self.generate_player_string(self.player_roles[a])
            players = plist[0]
            count = plist[2]
            embed.add_field(name=a[1]+" "+a[0]+" ("+str(count)+")", value=players, inline=True)

        embed.add_field(name="\u200b", value="\u200b", inline=False)
        plist = self.generate_player_string(self.tentative, False)
        players = plist[0]
        count = plist[2]
        embed.add_field(name=config.tentativeReact+" Tentative ("+str(count)+")", value=players, inline=True, )
        plist = self.generate_player_string(self.declined)
        players = plist[0]
        count = plist[2]
        embed.add_field(name=config.declinedReact+" Grounded ("+str(count)+")", value=players, inline=True)

        return embed

    def generate_edit_embed(self):
        embed = discord.Embed(title="0: "+self.title, description="1: "+self.description, timestamp=self.timeUTC)
        embed.add_field(name="Author", value=self.author[1], inline=False)
        time = str(self.timeUTC.timestamp()).split(".")[0]
        embed.add_field(name="2: Event Time: "+self.timeUTC.strftime("%b %d, %Y %H:%M:%S ZULU"), value="**Local Time: <t:" + time + ":f>**", inline=False)
        embed.add_field(name="3: Difficulty", value=str(self.difficulty) + "/10", inline=True)
        embed.add_field(name="4: Map", value=self.terrain, inline=True)
        embed.add_field(name="5: ModPack", value=self.modpack, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="6: Roles", value="\u200b", inline=False)
        for a in self.roles:
            embed.add_field(name=a[1]+" "+a[0], value="\u200b", inline=True)

        return embed

    def generate_summary(self):
        embed = discord.Embed(title=self.title, description="Summary for this event is as follows", timestamp=self.timeUTC)
        embed.add_field(name="Event Time", value=self.timeUTC.strftime("%m/%d/%Y, %H:%M:%S UTC"), inline=False)
        accepted = self.get_accepted_tentative_string()
        embed.add_field(name="Accepted("+str(accepted[1])+")", value=accepted[0], inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        for a in self.roles:
            plist = self.generate_player_string(self.player_roles[a], split_list=True)
            players = plist[0]
            count = plist[2]
            if count > 0:
                embed.add_field(name=a[1] + " " + a[0]+" ("+str(count)+")", value=players, inline=True)
        tentative = accepted = self.get_accepted_tentative_string(True)
        embed.add_field(name="Tentative("+str(tentative[1])+")", value=tentative[0], inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        for a in self.roles:
            plist = self.generate_player_string(self.player_roles[a], split_list=True)
            players = plist[1]
            count = plist[3]
            if count > 0:
                embed.add_field(name=a[1] + " " + a[0]+" ("+str(count)+")", value=players, inline=True)
        plist = self.generate_player_string(self.declined)
        players = plist[0]
        count = plist[2]
        embed.add_field(name="Declined ("+str(count)+")", value=players, inline=False)
        embed.set_footer(text="Local Time")
        return embed
