
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
# Redis Server started.  I use Redis just like I would environment variables.
# This way there are no secret keys or tokens laying around.
Client = discord.Client()
client = commands.Bot(command_prefix = "!")
redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)


# Sends messages to console and the default discord channel using on_ready
# If both messages appear then the Bot has started succesfully 
@client.event
async def on_ready():
    print("Discordis Bot Ready")
    




@client.event
async def on_member_join(member):
    # Find my Initiate role in order to add it as soon as a new user joins the server
    for server in client.servers:
        for role in server.roles:
            if role.name == 'Initiate':
                await client.add_roles(member, role)
                break
            else:
                continue
    # This role is limited to reading and writing txt in one channel.   The #welcome channel.
    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'welcome':
                # I put in an automatic way to remove the last 4 digits so the bot can properly greet our new member. 
                # We find the length of the members name and subtract 4 from that.  
                # Then we can use manual field variable specification to inject the number inside the message for proper splicing. 
                amount = len(member.name) - 4
                await client.send_message(channel, "Welcome to Senua Black {0:{1}}!!  If you're seeing this, you should have already received an invitation in Warframe to join our Clan. First off we need to know who you are.  Type your In-Game-Name exactly as it appears in Warframe then hit enter".format(member.name, amount))
                break
            else:
                continue
    # After the bot asks for the members IGN it gives the user a short amount of time to comply
    # If they type something in and hit enter it gets saved as an object called ign.
    ign = await client.wait_for_message(author=member)
    # If the timeout period kicks in then 'None' is returned instead of an object
    # If that happens the bot asks one more time for the user to enter there IGN.
    if ign.content == None:
        await client.send_message(member, "Before you can access our main text and voice channels or have access to our Dojo, you'll need to provide your IGN.  Please type in your IGN and hit enter inside the #welcome channel.")
        ign = await client.wait_for_message(author=message.name)
        # If the user still doesn't comply he/she is kicked but not banned. 
        if ign.content == None:
            kick(member)
        else:
            pass
    else:
        pass
    # If all goes well a new object will be instantiated with some of the data going into the SQL database
    # Using SQLAlchemy we call Session() into an object and now we can 'add' and 'commit'
    my_member = Member(user=str(ign.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set')
    session = Session()
    session.add(my_member)
    session.commit()
    # I plan on putting in a way to verify this is actually a real IGN that is a current member of our Clan
    # Until then, as long as the user types in something, he/she is automatically boosted to the role of Shadow Soldier and can access our main chat channels
    for server in client.servers:
        for role in server.roles:
            if role.name == 'Shadow Soldiers':
                await client.replace_roles(member, role)
                break
            else:
                continue
    # In order to protect the privacy of new users, all messages from the bot and the new user are purged from the channel
    # In its place is our list of rules and a short explanation for how to utilize our database.
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

@client.event
async def on_message(message):
    # First of three if statements that allow users to change their Planet, Quest and Priority
    if message.content.upper() == '$MYPLANET':
        await client.send_message(message.channel, "Please type the furthest Planet you've unlocked and hit enter.")
        planet = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(planet.author)).first() 

        # Check to see if member has been added to our database
        if current == None:
            # Initialize if not.  Only populate 'user' Column
            await client.send_message(message.channel, "Discordis needs to add you to The Database.  Please type your In-Game-Name and hit enter")
            ign = await client.wait_for_message(author=message.author)
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set')
            await client.send_message(message.channel, "Discordis found success in this endeavor.  Welcome to The Database {0}".format(ign.content))
        else:
            pass
        
        # Set the planet then commit to the database
        current.planet = str(planet.content)
        session.add(current)
        session.commit()
        # Print to console for verification
        print("User: {0} | IGN: {1} | Furthest Planet: {2} | Current Quest: {3} | Highest Priority: {4}".format(
                                                            current.user, current.ign, current.planet, current.quest, current.priority))
        
        # Let member know their changes have been saved.
        await client.send_message(message.channel, "{0} has been saved as the furthest Planet you've unlocked.  Use $MYSELF to see everything The Database knows about you.".format(current.planet))
    else:
	    pass

    # Second of three if statements
    if message.content.upper() == '$MYQUEST':
        await client.send_message(message.channel, "Please type the name of your current Quest and hit enter")
        quest = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(quest.author)).first() 

        if current == None:
            await client.send_message(message.channel, "Discordis needs to add you to The Database.  Please type your In-Game-Name and hit enter.")
            ign = await client.wait_for_message(author=message.author)
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set')
            await client.send_message(message.channel, "Discordis found success in this endeavor.  Welcome to The Database {0}".format(ign.content))
        else:
            pass
        
        current.quest = str(quest.content)
        session.add(current)
        session.commit()

        print("User: {0} | IGN: {1} | Furthest Planet: {2} | Current Quest: {3} | Highest Priority: {4}".format(
                                                            current.user, current.ign, current.planet, current.quest, current.priority))
        await client.send_message(message.channel, "{0} has been saved as your current Quest.    Use $MYSELF to see everything The Database knows about you.".format(current.quest))
    else:
	    pass
    
    # Third of three if statements
    if message.content.upper() == '$MYPRIORITY':
        await client.send_message(message.channel, "Please type the name of your current Quest and hit enter")
        priority = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(priority.author)).first() 

        if current == None:
            await client.send_message(message.channel, "Discordis needs to add you to The Database.  Please type your In-Game-Name and hit enter.")
            ign = await client.wait_for_message(author=message.author)
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set')
            await client.send_message(message.channel, "Discordis found success in this endeavor.  Welcome to The Database {0}".format(ign.content))
        else:
            pass
        
        current.priority = str(priority.content)
        session.add(current)
        session.commit()

        print("User: {0} | IGN: {1} | Furthest Planet: {2} | Current Quest: {3} | Highest Priority: {4}".format(
                                                            current.user, current.ign, current.planet, current.quest, current.priority))
        await client.send_message(message.channel, "{0} has been set as your top priority.   Use $MYSELF to see everything The Database knows about you.".format(current.priority))
    else:
	    pass


    # Command that allows members to set syndicates as roles for mentions.
    if message.content.upper() == '$ADDSYNDICATE':
        add_syndicate = await client.wait_for_message(author=message.author)
        syndicates = ('NEW LOKA', 'CEPHALON SUDA', 'STEEL MERIDIAN', 'RED VEIL', 'ARBITERS OF HEXIS', 'THE PERRIN SEQUENCE')
        if str(add_syndicate.content) in syndicates:
            for server in client.servers:
                for role in server.roles:
                    if role.name == str(add_syndicate.content):
                        await client.add_roles(message.author, role)
                        break
                    else:
                        continue
        else:
            await client.send_message(message.channel, "Make sure you type the syndicates name exactly how it is in Warframe.  Type $ADDSYNDICATE and try again.")
    else:
        pass

    if message.content.upper() == '$MYSELF':
        session = Session()
        self_object = session.query(Member).filter_by(user=str(message.author)).first()
        
        embed = discord.Embed(
            title = 'Warframe Status',
            description = 'Database Information For Members Of Senua Black',
            colour = discord.Colour.red()
        )
        
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.set_author(name=self_object.ign, icon_url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name="Furthest Planet", value=self_object.planet)
        embed.add_field(name="Current Quest", value=self_object.quest)
        embed.add_field(name="Biggest Priority", value=self_object.priority, inline=False)
        await client.send_message(message.channel, embed=embed)
    else:
        pass
    





# Using Redis to store my Discord Token.
client.run(redis_server.get('SENUA_TOKEN').decode('utf-8'))