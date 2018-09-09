
import asyncio
import time
import redis
import json

import discord
from discord.ext.commands import Bot
from discord.ext import commands
from urllib.request import Request, urlopen

from senua_db import Member, Session

# client will control the Bot commands and have access as if we were typing discord.Client
# Redis Server started
Client = discord.Client()
client = commands.Bot(command_prefix = "!")
redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)


# Sends messages to console and the default discord channel using on_ready
# If both messages appear then the Bot has started succesfully 
@client.event
async def on_ready():
    print("Discordis Bot Ready")
    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'welcome':
                await client.send_message(channel, "Discordis is waiting..")
                break
            else:
                continue

@client.event
async def on_member_join(member):

    for server in client.servers:
        for role in server.roles:
            if role.name == 'Initiate':
                await client.add_roles(member, role)
                break
            else:
                continue

    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'welcome':
                amount = len(member.name) - 4
                await client.send_message(channel, "Welcome to Senua Black {0:{1}}!!  If you're seeing this, you should \
                                                                                            have already received an invitation in Warframe to join our Clan. \
                                                                                            First off we need to know who you are.  Type your In-Game-Name \
                                                                                            exactly as it appears in Warframe then hit enter".format(member.name, amount))
                break
            else:
                continue

    ign = await client.wait_for_message(author=member)
    if ign.content == None:
        await client.send_message(member, "Before you can access our main text and voice channels \
                                                                                or even have access to our Dojo, you'll need to provide your IGN \
                                                                                Please type in your IGN and hit enter inside the #welcome channel")
        ign = await client.wait_for_message(author=member)
        if ign.content == None:
            kick(member)
        else:
            pass
    else:
        pass
    my_member = Member(user=str(member), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set')
    session = Session()
    session.add(my_member)
    session.commit()

    for server in client.servers:
        for role in server.roles:
            if role.name == 'Shadow Soldiers':
                await client.replace_roles(member, role)
                break
            else:
                continue
    
    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'welcome':
                await client.purge_from(channel, limit=100)
                await client.send_message(channel, " Our rules are simple.  If you stay inactive for longer than 14 days you'll be kicked from Discord and from Senua Black.  You can re-join later if you like.  Treat everyone with respect and try to be aware of where people are in the game.  This will help with squad building and avoiding massive spoilers.")

                await client.send_message(channel, "We have a tool to assist in just such endeavors. You can add what the furthest Planet you've unlocked is and what Quest you are currently tackling.  You can also add your biggest priority at the moment.  Farming Prime Parts, Building an Archwing, Getting through Nodes, etc. Just use these commands to add this information to your profile.  You'll also be able to search our database for other members who are doing similar things.")
                await client.send_message(channel,  "|  Furthest Planet: type  $MyPlanet    |  Current Quest: type    $MyQuest   |  Biggest Priority: type $MyPriority |")
                await client.send_message(channel, "The Planets only take In-Game Planets and The Quests only take In-Game Quests. But you can add whatever you want for your Biggest Priority.")
                                                                                
                break
            else:
                continue

    
    






client.run(redis_server.get('SENUA_TOKEN').decode('utf-8'))