import discord
from discord.ext.commands import Bot
from discord.ext import commands
import json
import asyncio
import time
import redis
from urllib.request import Request, urlopen


from our_db import Member, Session


Client = discord.Client()
client = commands.Bot(command_prefix = "!")
redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)

@client.event
async def on_ready():
    print("Penguins Are A Go")

@client.event
async def on_member_join(member):
    await client.send_message(member, "Please enter your In-Game-Name for Warframe")
    ign = await client.wait_for_message(member, author=member)
    member = Member(user=str(member), ign=str(ign.content), planet='Not Set', quest='Not Set')
    session = Session()
    session.add(member)
    session.commit()
    

@client.event
async def on_message(message):
    if message.content.upper() == "!SHOW":
        session = Session()
        current = session.query(Member).filter_by(user=str(message.author)).first()
        print(current)
    else:
        pass
    if message.content.upper() == "!PLANET":
        await client.send_message(message.channel, "What Planet are you currently at?")
        msg = await client.wait_for_message(author=message.author)
        member = Member(user=message.author, ign=message.author, planet=msg.content, quest=msg.content)
        await client.send_message(message.channel, member)
    else:
        pass
    if message.content.upper() == "MYPLANET":
        red_ans = redis_server.get("{0}_PLANET".format(message.author))
        await client.send_message(message.channel, red_ans )
    else:
        pass
    if message.content.upper() == "*MYIGN":
        await client.send_message(message.channel, "What Planet are you currently at?")
        msg = await client.wait_for_message(author=message.author)
        redis_author = '{0}_PLANET'.format(message.author)
        print (redis_author)
        redis_server.set(redis_author, msg.content)
    if message.content.upper() == "MYIGN":
        red_ans = redis_server.get("{0}_PLANET".format(message.author))
        await client.send_message(message.channel, red_ans )
    else:
        pass








client.run("NDg1MTE2NzMzMTg3OTQ4NTY0.DmsbkA.19qas06G46I6vv9aqbG9-0wm5Mg")
