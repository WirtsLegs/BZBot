# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import discord
import events
import asyncio
import config
import dateparser
import pytz
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot("$")
bot.bot_channel = config.bot_channel
bot.mission_channel = config.mission_channels


active_events = {}


@bot.command(name="ping")
async def ping(ctx):
    await ctx.channel.send("pong")


@bot.command(name="event")
async def event(ctx):
    if not ctx.channel.id in config.mission_channels:
        return
    dmChannel = await ctx.author.send("It looks like you're trying to create a mission...")

    def check(message):
        return message.author == ctx.author and message.channel == dmChannel.channel

    async def askMultChoice(question, description, options, timeout=60):
        rng = range(len(options))
        if description is not None:
            emb = discord.Embed(title=question, description=description)
        else:
            emb = discord.Embed(title=question)
        emb.set_footer(text="type 'cancel' to cancel mission creation")

        for i in rng:
            emb.add_field(name=str(i) + " : " + options[i], value="\u200b", inline=False)
        await ctx.author.send(embed=emb)
        print("Waiting for reply...")
        user_reply = await bot.wait_for('message', check=check, timeout=20.0)
        print("User replied")
        try:
            reply = int(user_reply.content)
        except ValueError:
            if user_reply.content == "cancel":
                return False
        else:
            if reply in rng:
                return options[int(user_reply.content)]
            else:
                await ctx.author.send("invalid response, please select from the available options")
                result = await askMultChoice(question, options)
                return result

    async def askYesNoQuestion(question, descrip=None, timeout=60):
        emb = discord.Embed(title=question, description=("\u200b" if descrip is None else descrip))
        emb.set_footer(text="type 'cancel' to cancel mission creation")
        await ctx.author.send(embed=emb)
        print("Waiting for reply...")
        user_reply = await bot.wait_for('message', check=check, timeout=20.0)
        print("User replied")
        reply = user_reply.content
        reply = reply if not reply == "cancel" else False
        if not reply:
            return False
        return reply if reply == "yes" else "no"

    async def askQuestion(question, descrip=None, timeout=60):
        emb = discord.Embed(title=question, description=("\u200b" if descrip is None else descrip))
        emb.set_footer(text="type 'cancel' to cancel mission creation")
        await ctx.author.send(embed=emb)
        print("Waiting for reply...")
        user_reply = await bot.wait_for('message', check=check, timeout=20.0)
        print("User replied")
        reply = user_reply.content
        return reply if not reply == "cancel" else False

    async def askDateTimeQuestion(question, descrip=None, timeout=60):
        emb = discord.Embed(title=question, description=("\u200b" if descrip is None else descrip))
        emb.set_footer(text="type 'cancel' to cancel mission creation")
        await ctx.author.send(embed=emb)
        print("Waiting for reply...")
        user_reply = await bot.wait_for('message', check=check, timeout=20.0)
        print("User replied")
        reply = user_reply.content
        if reply == "cancel":
            return False
        try:
            d = dateparser.parse(reply)
            if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
                d = d.replace(tzinfo=pytz.utc)

        except ValueError:
            return askDateTimeQuestion(question, descrip, timeout)
        else:
            return d

    try:
        event_args = {"author": ctx.author.display_name}
        for q in config.question_list:
            reply = ""
            if q[4] == 0:
                reply = await askQuestion(q[1], q[2], q[3])
            elif q[4] == 1:
                reply = await askMultChoice(q[1], q[2], q[5], q[3])
            elif q[4] == 2:
                reply = await askYesNoQuestion(q[1], q[2], q[3])
            elif q[4] == 3:
                reply = await askDateTimeQuestion(q[1], q[2], q[3])
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
        ev = events.Event(event_args)
        em = ev.generateEmbed()
        event_msg = await ctx.channel.send(embed=em)
        active_events[event_msg.id] = ev


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
