# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import discord
import events
import asyncio
import config
import questions
import dateparser
import pytz
import dill
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot("$", intents=intents)
bot.bot_channel = config.bot_channel
bot.mission_channel = config.mission_channels

active_events = {}


@bot.command(name="ping")
async def ping(ctx):
    await ctx.channel.send("pong")


@bot.command(name="event")
async def event(ctx):
    if ctx.channel.id not in config.mission_channels:
        return
    dmChannel = await ctx.author.send("It looks like you're trying to create a mission...")

    try:
        event_args = {"author": (ctx.author.id, ctx.author.display_name)}
        info = (ctx.author, bot, dmChannel.channel)
        for q in config.question_list:
            reply = ""
            if q[4] == 0:
                reply = await questions.askQuestion(info, q[1], q[2], q[3])
            elif q[4] == 1:
                reply = await questions.askMultChoice(info, q[1], q[2], q[5], q[3])
            elif q[4] == 2:
                reply = await questions.askYesNoQuestion(info, q[1], q[2], q[3])
            elif q[4] == 3:
                reply = await questions.askDateTimeQuestion(info, q[1], q[2], q[3])
            elif q[4] == 4:
                print(q[5])
                reply = await questions.gatherRoles(info, q[1], q[2], q[5], q[3])
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
        em = ev.generateEmbed()
        event_msg = await ctx.channel.send(embed=em)
        for a in ev.roles:
            await event_msg.add_reaction(a[1])
        await event_msg.add_reaction(config.tentativeReact)
        await event_msg.add_reaction(config.declinedReact)
        await event_msg.add_reaction(config.deleteReact)
        await event_msg.add_reaction(config.editReact)
        active_events[event_msg.id] = ev
        ev.eID = str(event_msg.id)
        with open(ev.eID+".pkl", 'wb') as outf:
            dill.dump(ev, outf, protocol=0)
        await ctx.message.delete()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')



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
        handle = await active_events[msgid].react_handle(payload.emoji, message, user, bot)
        if handle:
            with open(str(msgid)+".pkl", 'wb') as outf:
                dill.dump(active_events[msgid], outf, protocol=0)


for file in os.listdir("./"):

    if file.endswith(".pkl"):
        with open(file,"rb") as f:
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
