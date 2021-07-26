# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from os import path
import discord
import events
import asyncio
import config
import questions
import datetime
import pytz
import dill
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot("$", intents=intents)
bot.bot_channel = config.bot_channel
bot.mission_channels = config.mission_channels

active_events = {}

if path.exists("missionchannels.cfg"):
    with open("missionchannels.cfg", "r") as f:
        lines = [int(line.strip()) for line in f]
    config.mission_channels=lines


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("bot is using discord version: " + discord.__version__)
    #bot.loop.create_task(time_management())
    time_management.start()


@tasks.loop(seconds=30)
async def time_management():
    for e in list(active_events.keys()):
        e_time = active_events[e].timeUTC
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        remaining = (e_time - now).total_seconds()

        if remaining < (-1*config.event_auto_delete):
            chan = bot.get_channel(active_events[e].channel)
            message = await chan.fetch_message(e)
            await message.delete()
            active_events.pop(e)
            os.remove(str(e) + ".pkl")
        elif not active_events[e].reminderSent and remaining < config.event_reminder:
            print("reminder time")
            chan = bot.get_channel(active_events[e].channel)
            message = await chan.fetch_message(e)
            url = message.jump_url
            minutes = remaining // 60
            await active_events[e].send_message(bot, "Notice to Move",
                                                "A mission you have signed up for starts in " + str(
                                                    minutes).split(".")[0] + " minutes!: [" + active_events[
                                                    e].title + "](" + url + ")", accepted=True, tentative=False)
            await active_events[e].send_message(bot, "Notice to Move",
                                                "A mission you are tentative on is starting in " + str(
                                                    minutes).split(".")[0] + " minutes, please follow the link to confirm attendance: [" +
                                                active_events[e].title + "](" + url + ")", accepted=False,
                                                tentative=True)
            active_events[e].reminderSent = True
            active_events[e].write_event()



@bot.command(name="missionchannel")
@has_permissions(administrator=True)
async def mission_channel(ctx):
    chID = ctx.channel.id
    emb = None
    if chID in config.mission_channels:
        config.mission_channels.remove(chID)
        emb = discord.Embed(title="Channel removed from mission channels", description="The following are the currently active mission channels")
    else:
        config.mission_channels.append(chID)
        emb = discord.Embed(title="Channel added to mission channels", description="The following are the currently active mission channels")

    for c in config.mission_channels:
        emb.add_field(name=bot.get_channel(c).name, value="\u200b")

    await ctx.author.send(embed=emb)
    await ctx.message.delete()
    with open("missionchannels.cfg", "w") as f:
        for c in config.mission_channels:
            f.write('%s\n' % str(c))


@bot.command(name="ping")
async def ping(ctx):
    await ctx.channel.send("pong")

@bot.command(name="purge")
@has_permissions(administrator=True)
async def purge(ctx):
    print("got purge command")
    #if not any(item.id in config.admin_roles for item in ctx.author.roles):
    #    print("not admin")
    #    return
    dmChannel = None
    def check(message):
        return message.author == ctx.author and message.channel == dmChannel.channel

    guild = ctx.message.guild

    to_kick_new = []
    to_kick_ghost = []
    #ctx.message.author.guild_permissions.administrator
    for member in guild.members:
        if member.bot or member.guild_permissions.administrator:
            continue
        kick_newbro = False
        kick_ghost = False
        age = datetime.date.today() - member.joined_at.date()
        if age.days > 30:
            if not any(item.id in config.one_month for item in member.roles):
                kick_newbro = True
                kick_ghost = False
        if age.days > 7:
            if not any(item.id in config.one_week for item in member.roles):
                kick_ghost = True
                kick_newbro = False

        if kick_newbro:
            to_kick_new.append(member)
        elif kick_ghost:
            to_kick_ghost.append(member)
    emb = discord.Embed(title="The following members will be kicked:", description="Please indicate yes or no if you would like to kick")
    ghosted = ""
    count = 0
    for target in to_kick_ghost:
        ghosted = ghosted + target.mention + "  "
        if count == 4:
            ghosted = ghosted + "\n"
            count = 0
    emb.add_field(name="Ghosted:", value=ghosted if len(ghosted) > 0 else "\u200b")
    newcomers = ""
    count = 0
    for target in to_kick_new:
        newcomers = newcomers + target.mention + "  "
        if count == 4:
            newcomers = newcomers + "\n"
            count = 0
    emb.add_field(name="Newcomers:", value=newcomers if len(newcomers) > 0 else "\u200b")
    dmChannel = await ctx.author.send(embed=emb)

    user_reply = await bot.wait_for('message', check=check, timeout=120)

    reply = user_reply.content
    reply = True if reply.lower() == "yes" else False
    if reply:

        for u in (to_kick_new+to_kick_ghost):
            try:
                await u.send(embed=discord.Embed(title="You have been kicked", description=config.kick_reason))
                await u.kick(reason="kicked by bot for inactivity")
            except:
                continue

        emb = discord.Embed(title="Purge Complete")
        await ctx.author.send(embed=emb)

@bot.command(name="event")
async def event(ctx):
    if ctx.channel.id not in config.mission_channels:
        return
    dmChannel = await ctx.author.send("It looks like you're trying to create a mission...")

    try:
        event_args = {"author": (ctx.author.id, ctx.author.display_name)}
        event_args['channel'] = ctx.channel.id
        info = (ctx.author, bot, dmChannel.channel)
        for q in config.question_list:
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
                reply = await questions.gatherRoles(info, q[1], q[2], q[5], timeout=q[3])
                print(reply)
            if not reply:
                emb = discord.Embed(title="Right, well fuck you too!")
                await ctx.author.send(embed=emb)
                return
            event_args[q[0]] = reply

    except asyncio.TimeoutError:
        await ctx.author.send(
            "You dirty motherfucker! You ignored me!!??\nI'll have you know I graduated top of my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I'm the top sniper in the entire US armed forces. You are nothing to me but just another target.")
        return
    else:
        ev = events.DCSEvent(event_args)
        em = ev.generate_embed()
        event_msg = await ctx.channel.send(embed=em)
        for a in ev.roles:
            await event_msg.add_reaction(a[1])
        await event_msg.add_reaction(config.tentativeReact)
        await event_msg.add_reaction(config.declinedReact)
        await event_msg.add_reaction(config.configReact)
        active_events[event_msg.id] = ev
        ev.eID = str(event_msg.id)
        with open(ev.eID + ".pkl", 'wb') as outf:
            dill.dump(ev, outf, protocol=0)
        emb = discord.Embed(title="Mission Posted",
                             description="Your mission has been posted: [" + ev.title + "](" + event_msg.jump_url + ")")
        await ctx.author.send(embed=emb)
        await ctx.message.delete()


@bot.event
async def on_message(message):
    if message.channel.id == bot.bot_channel:
        if message.content == "hello":
            # SENDS BACK A MESSAGE TO THE CHANNEL.
            await message.channel.send("hey dirtbag")
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    msgid = payload.message_id
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    if msgid in active_events.keys():
        handle = await active_events[msgid].react_handle(payload.emoji, message, payload.member, user, bot)
        if handle == True:
            with open(str(msgid) + ".pkl", 'wb') as outf:
                dill.dump(active_events[msgid], outf, protocol=0)
        elif handle == "DELETE":
            await message.delete()
            active_events.pop(msgid)
            os.remove(str(msgid) + ".pkl")
        elif handle == "MOVED":
            await message.delete()
            ev = active_events.pop(msgid)
            active_events[ev.eID] = ev
            os.remove(str(msgid) + ".pkl")
            ev.write_event()


for file in os.listdir("./"):

    if file.endswith(".pkl"):
        with open(file, "rb") as f:
            active_events[int(file.split(".")[0])] = dill.load(f)

bot.run(TOKEN)

# class bot(commands.Bot('-')):
#    bot_channel = ""
#    async def on_ready(self):
#        print(f'{self.user} has connected to Discord!')
#        self.bot_channel = int(os.getenv('bot_channel'))


# if __name__ == '__main__':
#    load_dotenv()
#    TOKEN = os.getenv('DISCORD_TOKEN')
#    client = bot()
#    print("connecting maybe")
#    client.run(TOKEN)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
