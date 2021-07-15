import discord
import dateparser
import pytz
import tzlocal
import config


async def askMultChoice(info_tuple, question, description, options, timeout=60):#infortuple=(user,bot,channel)
    rng = range(len(options))

    def check(message):
        return message.author == info_tuple[0] and message.channel == info_tuple[2]

    if description is not None:
        emb = discord.Embed(title=question, description=description)
    else:
        emb = discord.Embed(title=question)
    emb.set_footer(text="type 'cancel' to cancel mission creation")

    for i in rng:
        emb.add_field(name=str(i) + " : " + options[i], value="\u200b", inline=False)
    await info_tuple[0].send(embed=emb)
    print("Waiting for reply...")
    user_reply = await info_tuple[1].wait_for('message', check=check, timeout=timeout)
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
            await info_tuple[0].send("invalid response, please select from the available options")
            result = await askMultChoice(question, description, options, timeout)
            return result


async def askYesNoQuestion(info_tuple, question, descrip=None, timeout=60):

    def check(message):
        return message.author == info_tuple[0] and message.channel == info_tuple[2]

    emb = discord.Embed(title=question, description=("\u200b" if descrip is None else descrip))
    emb.set_footer(text="type 'cancel' to cancel mission creation")
    await info_tuple[0].send(embed=emb)
    print("Waiting for reply...")
    user_reply = await info_tuple[1].wait_for('message', check=check, timeout=20.0)
    print("User replied")
    reply = user_reply.content
    reply = reply if not reply == "cancel" else False
    if not reply:
        return False
    return "Yes" if reply.lower() == "yes" else "No"


async def askQuestion(info_tuple, question, descrip=None, timeout=60):

    def check(message):
        return message.author == info_tuple[0] and message.channel == info_tuple[2]

    emb = discord.Embed(title=question, description=("\u200b" if descrip is None else descrip))
    emb.set_footer(text="type 'cancel' to cancel mission creation")
    await info_tuple[0].send(embed=emb)
    print("Waiting for reply...")
    user_reply = await info_tuple[1].wait_for('message', check=check, timeout=20.0)
    print("User replied")
    reply = user_reply.content
    return reply if not reply == "cancel" else False


async def askDateTimeQuestion(info_tuple, question, descrip=None, timeout=60):

    def check(message):
        return message.author == info_tuple[0] and message.channel == info_tuple[2]

    emb = discord.Embed(title=question, description=("\u200b" if descrip is None else descrip))
    emb.set_footer(text="type 'cancel' to cancel mission creation")
    await info_tuple[0].send(embed=emb)
    print("Waiting for reply...")
    user_reply = await info_tuple[1].wait_for('message', check=check, timeout=20.0)
    print("User replied")
    reply = user_reply.content
    print(reply)
    if reply == "cancel":
        return False
    try:
        d = dateparser.parse(reply, settings={'PREFER_DATES_FROM': 'future', 'RETURN_AS_TIMEZONE_AWARE': True})
        print(d)
        if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
            tz = tzlocal.get_localzone()
            d = d.replace(tzinfo=tz)
        d = d.astimezone(pytz.utc)


    except ValueError:
        return askDateTimeQuestion(question, descrip, timeout)
    else:
        return d


async def gatherRoles(info_tuple, question, description, options, timeout=60, roles=None):

    def check(message):
        return message.author == info_tuple[0] and message.channel == info_tuple[2]

    keys = list(options.keys())
    rng = range(len(keys))
    if roles is None:
        roles = []
    if description is not None:
        emb = discord.Embed(title=question, description=description)
    else:
        emb = discord.Embed(title=question)
    emb.set_footer(text="type 'done' when all roles selected, type 'cancel' to cancel mission creation")

    for i in rng:
        if keys[i] in roles:
            emb.add_field(name=str(i) + " : " + options[keys[i]] + "-selected", value="\u200b", inline=True)
        else:
            emb.add_field(name=str(i) + " : " + options[keys[i]], value="\u200b", inline=True)
    await info_tuple[0].send(embed=emb)
    print("Waiting for reply...")
    user_reply = await info_tuple[1].wait_for('message', check=check, timeout=20.0)
    print("User replied")
    try:
        reply = int(user_reply.content)
    except ValueError:
        if user_reply.content == "cancel":
            return False
        elif user_reply.content == "done":
            return roles
    else:
        if reply in rng:
            if not keys[reply] in roles:
                roles.append(keys[reply])
            else:
                roles.remove(keys[reply])
            print(roles)
            result = await gatherRoles(info_tuple, question, description, options, timeout, roles)
            return result
        else:
            await info_tuple[0].send("invalid response, please select from the available options")
            result = await gatherRoles(info_tuple, question, description, options, timeout, roles)
            return result
