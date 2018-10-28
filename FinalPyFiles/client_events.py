
import asyncio
import time
import redis
import json

import discord
from discord.ext.commands import Bot
from discord.ext import commands
from urllib.request import Request, urlopen

from senua_db import Member, Session, Base, engine


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
            if role.name == 'New Arrival':
                await client.add_roles(member, role)
                break
            else:
                continue
    # This role is limited to reading and writing txt in one channel.   The #welcome channel.
	# We find the length of the members name and subtract 4 from that.  
    # Then we can use manual field variable specification to inject the number inside the message for proper splicing. 
    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'welcome':
                await client.purge_from(channel, limit=100)
                amount = len(member.name) - 4
                await client.send_message(channel, "Welcome to Senua Black {0:{1}}!!  If you're seeing this, you should have already received an invitation in Warframe to join our Clan.   Now that you're here, we need to know who you are.  Please type your In-Game-Name exactly as it appears in Warframe then hit enter".format(member.name, amount))
                break
            else:
                continue
	# We save the user response as an object named ign
	# If timeout occurs, 'None' is returned instead of an object
    # The bot asks one more time for the user to enter there IGN.
    ign = await client.wait_for_message(author=member)

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

    # Using SQLAlchemy we call Session() into an object and now we can 'add' and 'commit' our newest member
    newMember = Member(user=str(ign.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
    session = Session()
    session.add(newMember)
    session.commit()
    
    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'warframe':
                await client.send_message(channel, "Please welcome {0} to Senua Black.  They are known as {1} in Warframe. ".format(ign.author, ign.content))
                break
            else:
                continue
	# Now that we have the users IGN we change their role from New Arrival to Initiate
    for server in client.servers:
        for role in server.roles:
            if role.name == 'Initiate':
                await client.replace_roles(member, role)
                break
            else:
                continue

    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'welcome':
                await client.purge_from(channel, limit=100)
                embed = discord.Embed(
                colour = discord.Colour.red()
                )
                senuaMission = "Our goal is to recruit and retain active Warframe players who will join us in helping anyone and everyone with whatever the endeavor may be while also furthering our own achievments as well.  \n \n Senua Black accepts anyone who wants to join.  We will all move forward together even if our personal goals are quite different.  We encourage higher ranking players to lend assistance when asked.  If you are a low ranking player, you  should never feel intimedated or inadequate.  We want you to feel comfortable asking questions and engaging in conversations. \n \n You are now an Initiate and you can join most of our channels.   \n #warframe is our main text channel.  \n #fashionframe is where we post screenshots of our gorgeous frames.   \n #discordis will introduce you to Discordis and show you what commands you can use.  \n \n Thanks so much for joining Senua Black!!"
                embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
                embed.add_field(name="Senua Black", value=senuaMission)
                await client.send_message(channel, embed=embed)
                break
            else:
                continue

@client.event
async def on_message(message):

    if message.content.upper() == '$INFO':
        embed = discord.Embed(
        colour = discord.Colour.red()
        )
        botInfo = "Discordis is our in-house bot that is able to take information from you at any time and save it to your Senua Black profile.  \n \n $PLANET - The furthest planet you've reached so far.\n $QUEST - The current Warframe Quest you are tackling.\n $PRIORITY -  What you are currently fixated on more than anything else in Warframe.\n $SYNDICATE - Enter one Syndicate that you are affiliated with.  This also assigns you a Syndicate Role that is mentionable.\n\n $FIND - Type in the In-Game-Name of a Senua Black member and retrieve any information that individual has saved.\n $ALL - Displays a list of all Senua Black members with any information they have saved.\n $MYSELF - Displays your own personal information."
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name="Discordis", value=botInfo)
        await client.send_message(message.channel, embed=embed)
    else:
        pass




    # First of three if statements that allow users to change their Planet, Quest and Priority
    if message.content.upper() == '$PLANET':
        await client.send_message(message.channel, "Please type the furthest Planet you've unlocked and hit enter.")
        planet = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(planet.author)).first() 

        # Check to see if member has been added to our database
        if current == None:
            # Initialize if not.  Only populate 'user' Column
            await client.send_message(message.channel, "Discordis needs to add you to The Database.  Please type your In-Game-Name and hit enter")
            ign = await client.wait_for_message(author=message.author)
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            await client.send_message(message.channel, "Discordis found success in this endeavor.  Welcome to The Database {0}".format(ign.content))
        else:
            pass
        
        # Set the planet then commit to the database
        current.planet = str(planet.content)
        session.add(current)
        session.commit()
        # Print to console for verification
        print("User: {0} | IGN: {1} | Furthest Planet: {2} | Current Quest: {3} | Highest Priority: {4} | Syndicate: {5}".format(
                                                            current.user, current.ign, current.planet, current.quest, current.priority, current.syndicate))
        
        # Let member know their changes have been saved.
        await client.send_message(message.channel, "{0} has been saved as the furthest Planet you've unlocked.  Use $MYSELF to see everything The Database knows about you.".format(current.planet))
    else:
	    pass

    # Second of three if statements
    if message.content.upper() == '$QUEST':
        await client.send_message(message.channel, "Please type the name of your current Quest and hit enter")
        quest = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(quest.author)).first() 

        if current == None:
            await client.send_message(message.channel, "Discordis needs to add you to The Database.  Please type your In-Game-Name and hit enter.")
            ign = await client.wait_for_message(author=message.author)
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            await client.send_message(message.channel, "Discordis found success in this endeavor.  Welcome to The Database {0}".format(ign.content))
        else:
            pass
        
        current.quest = str(quest.content)
        session.add(current)
        session.commit()

        print("User: {0} | IGN: {1} | Furthest Planet: {2} | Current Quest: {3} | Highest Priority: {4} | Syndicate: {5}".format(
                                                            current.user, current.ign, current.planet, current.quest, current.priority, current.syndicate))
        await client.send_message(message.channel, "{0} has been saved as your current Quest.    Use $MYSELF to see everything The Database knows about you.".format(current.quest))
    else:
	    pass
    
    # Third of three if statements
    if message.content.upper() == '$PRIORITY':
        await client.send_message(message.channel, "Please type the name of your current Quest and hit enter")
        priority = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(priority.author)).first() 

        if current == None:
            await client.send_message(message.channel, "Discordis needs to add you to The Database.  Please type your In-Game-Name and hit enter.")
            ign = await client.wait_for_message(author=message.author)
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            await client.send_message(message.channel, "Discordis found success in this endeavor.  Welcome to The Database {0}".format(ign.content))
        else:
            pass
        
        current.priority = str(priority.content)
        session.add(current)
        session.commit()

        print("User: {0} | IGN: {1} | Furthest Planet: {2} | Current Quest: {3} | Highest Priority: {4} | Syndicate: {5}".format(
                                                            current.user, current.ign, current.planet, current.quest, current.priority, current.syndicate))
        await client.send_message(message.channel, "{0} has been set as your top priority.   Use $MYSELF to see everything The Database knows about you.".format(current.priority))
    else:
	    pass


    # Command that allows members to set syndicates as roles for mentions.
    if message.content.upper() == '$SYNDICATE':
        await client.send_message(message.channel, "Type in the name of a Syndicate you would like to add and hit enter.  Make sure you type it in exactly as it appears in the game: New Loka, Cephalon Suda, Steel Meridian, Red Veil, Arbiters Of Hexis, The Perrin Sequence")
        add_syndicate = await client.wait_for_message(author=message.author)
        syndicate_str = str(add_syndicate.content)
        syndicates = ('NEW LOKA', 'CEPHALON SUDA', 'STEEL MERIDIAN', 'RED VEIL', 'ARBITERS OF HEXIS', 'THE PERRIN SEQUENCE')
        if syndicate_str.upper() in syndicates:
            for server in client.servers:
                for role in server.roles:
                    if role.name.upper() == syndicate_str.upper():
                        await client.add_roles(message.author, role)
                        new_role = role.name
                        break
                    else:
                        continue
            await client.send_message(message.channel, "You have succesfully added {0} as a mentionable role with Discord.  What level are you currently at with this syndicate?".format(new_role))
            level = await client.wait_for_message(author=message.author)
            level_str = str(level.content)
            level_int = [int(s) for s in level_str.split() if s.isdigit()][0]
            await client.send_message(message.channel, "Just to make sure everything is correct.  You are in {0} and are currently at Level {1}. Is this correct? Type Yes or No".format(new_role, level_int))
            answer = await client.wait_for_message(author=message.author)
            if str(answer.content).upper() == 'YES':
                session = Session()
                current = session.query(Member).filter_by(user=str(answer.author)).first()
                if current == None:
                    await client.send_message(message.channel, "Discordis needs to add you to The Database.  Please type your In-Game-Name and hit enter.")
                    ign = await client.wait_for_message(author=message.author)
                    current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
                    await client.send_message(message.channel, "Discordis found success in this endeavor.  Welcome to The Database {0}".format(ign.content))
                else:
                    pass
                current.syndicate = "Level {0}, {1}".format(level_int,  syndicate_str)
                session.add(current)
                session.commit()
                await client.send_message(message.channel, "Information has been saved to The Database. ")
            else:
                await client.send_message(message.channel,  "Then try again.  Further development needed to assist midway through.  Try starting over with $SYNDICATE  Make sure you type in everything correctly and have only 1 number that is 0-5 for you Level.    If you still have issues please let me know  - withinmyself")
        else:
            await client.send_message(message.channel, "Make sure you type the syndicates name exactly how it is in Warframe (Use the given reference list).  Type $SYNDICATE and try again.")
    else:
        pass

    if message.content.upper() == '$FIND':
        await client.send_message(message.channel, "Type in the IGN of the member you'd like to look up")
        current_ign = await client.wait_for_message(author=message.author)
        ign_str = str(current_ign.content)
        session = Session()
        self_object = session.query(Member).filter_by(ign=ign_str).first()
        
        
        embed = discord.Embed(
            title = 'Warframe Status',
            description = 'Database Information For Members Of Senua Black',
            colour = discord.Colour.red()
        )
        
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.set_author(name=self_object.ign, icon_url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name="Furthest Planet", value=self_object.planet)
        embed.add_field(name="Current Quest", value=self_object.quest)
        embed.add_field(name="Syndicates", value=self_object.syndicate)
        embed.add_field(name="Biggest Priority", value=self_object.priority, inline=False)
        await client.send_message(message.channel, embed=embed)
    else:
        pass
    





# Using Redis to store my Discord Token.
client.run(redis_server.get('SENUA_TOKEN').decode('utf-8'))