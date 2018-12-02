import asyncio
import time
import redis
import json
import random
import os

import discord
from discord.ext.commands import Bot
from discord.ext import commands
from urllib.request import Request, urlopen

from senua_db import Member, Session, Base, engine
from strings import botInfo, welcome, ignAdd, \
    addMember, syndicateRole, syndicates, tryAgain, success, \
    recruitMessage, rulesOne, rulesTwo, titles, missionStatement, \
    welcomeMessage, contest, rivenList


Client = discord.Client()
client = commands.Bot(command_prefix = "!")
redis_server = redis.StrictRedis(host='localhost', port=6379, db=0, password=os.environ.get('REDISAUTH'))


# Verify functionality  
debug=True


@client.event
async def on_ready():
    print("Discordis Bot Ready")
    redis_server.set('ARRIVAL_COUNT', 0)  # Track users who are currently joining  



@client.event
async def on_member_join(member):
#    Triggered when a new member joins.  

#    First they are assigned the 'New Arrival' Role.  
#    Our invite puts new members in a channel called '#purgatory'.
#    The '#welcome' channel is renamed to '#welcome_MEMBER_NAME'.  
#    The 'New Arrival' Role only allows access to '#purgatory' & '#welcome_MEMBER_NAME'.  
#    There is information in '#purgatory' that explains a few things to the new member.
#    Obove all else, they are instructed to move to the welcome channel with their name attached.
#    In here they are asked to type in their In-Game-Name and hit [ENTER]
#    A new database record is created for the user with the 'user' and 'ign' fields popluated correctly.  
#    The rest of the fields initialize as 'Not Set'.
#    The member is automatically promoted to 'Initiate' which allows them access to our main channels.  
#    The '#welcome' channel is recreated and set up for future New Arrivals. 
#    And finally a welcome message is sent to '#warframe' letting current members know about our New Arrival.  



    redis_server.incr('ARRIVAL_COUNT')
    x = redis_server.get('ARRIVAL_COUNT')

    # Search for 'New Arrival' Role and apply to new member.  

    for server in client.servers:
        for role in server.roles:
            if role.name == 'New Arrival':
                await client.add_roles(member, role)
                break
            else:
                continue
        break

    # Search for '#welcome' channel and rename it by adding members name to the end.  

    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'welcome':
                await client.purge_from(channel, limit=100)
                try:
                    redis_server.set('WELCOME{0}'.format(str(x)), 'welcome_{0:{1}}'.format(member.name, len(member.name) - 4))
                    redis_server.set('USER{0}'.format(str(x)), '{0:{1}}'.format(member.name, len(member.name) - 4))
                    await client.edit_channel(channel, name=redis_server.get('WELCOME{0}'.format(x)).decode('utf-8'))
                    await client.send_message(channel,welcome.format(
                                            member.name, len(member.name) - 4))
                    break
                except ValueError(e):
                    await client.edit_channel(channel, name=redis_server.get('WELCOME{0}'.format(x)).decode('utf-8'))
                    await client.send_message(channel,welcome.format(
                                            member.name, len(member.name) - 4))
                    print('ValueError -> {0}'.format(e))
                    break
            else:
                continue
        break

    # Set up '#welcome' for future New Arrivals.  

    for server in client.servers:
        for role in server.roles:
            if role.name == 'New Arrival':
                denyAccess = discord.PermissionOverwrite(read_messages=False, send_messages=False)
                newArrival = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                await client.create_channel(server, 'welcome',  (role, newArrival), (server.me, newArrival), (server.default_role, denyAccess))
                break
            else:
                continue
        break

    # Accept the members In-Game-Name as variable ign.  
    
    ign = await client.wait_for_message(author=member)

    # Ask user to try again if no response is given.  

    if len(ign.content) > 30:
        await client.send_message(member, "Too many characters.  That is most likely not your In-Game-Name for Warframe.  Please use the same invite code and try again.")
        await client.kick(member)
    else:
        pass
    if ign.content == None:
        await client.send_message(member, ignAdd)
        ign = await client.wait_for_message(author=message.name)

        # If the user still doesn't respond he/she is kicked but not banned. 

        if ign.content == None:
            await client.kick(member)
        else:
            pass
    else:
        pass

    # Delete the temporary channel which will automatically drop them in our main txt channel, '#warframe'.  
    
    await client.delete_channel(ign.channel)

    # Save new member into SQL using SQLAlchemy.  
    if len(ign.content) <= 30:
        newMember = Member(user=str(ign.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
        session = Session()
        session.add(newMember)
        session.commit()
    
    # Send welcome message to main channel for everyone to see that a new member has joined.  

        for server in client.servers:
            for channel in server.channels:
                if channel.name == 'warframe'    :
                    await client.send_message(channel, "Please welcome {0} to Senua Black.  They are known as {1} in Warframe.  Remember to use $INFO for Helpful Information or $HELP for a list of all our cool Bot commands.".format(redis_server.get('USER{0}'.format(x)).decode('utf-8'),  str(newMember.ign)))
                    break
                else:
                    continue
    # Assign the role of Initiate so they can read/write in our main channel.  

        for server in client.servers:
            for role in server.roles:
                if role.name == 'Initiates':
                    await client.replace_roles(member, role)
                    break
                else:
                    continue
            break
    else:
        pass
    # Revisit!!  

    for server in client.servers:
        for channel in server.channels:
            if debug == True:
                print(channel.name)
            else:
                pass
            if channel.name == redis_server.get('WELCOME{0}'.format(x)).decode('utf-8'):
                await client.delete_channel(channel)
                if debug == True:
                    print("made it to delete")
                break
            else:
                if debug == True:
                    print("else iteration")
                continue
        break
    if debug == True:
        print("CLEAR")
    else:
        pass

    # Send private embed messages to new user with rules and bot commands.  

    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
    embed.add_field(name="Senua Black", value=missionStatement)
    await client.send_message(member, embed=embed)
    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/priNXCM.jpg')
    embed.add_field(name="Discordis", value=botInfo)
    await client.send_message(member, embed=embed)
    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
    embed.add_field(name="Guidelines For Senua Black", value=rulesOne)
    await client.send_message(member, embed=embed)
    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
    embed.add_field(name="Guidelines For Senua Black", value=rulesTwo)
    await client.send_message(member, embed=embed)

    # Reset joining members to 0.  
    
    redis_server.set('ARRIVAL_COUNT', 0)


@client.event
async def on_message(message):
# Several keywords to listen for that trigger different events.
# 
# DETAILS
# $INFO - Senua Black Information
# $BOT - Bot Commands
# $RECRUIT - Display Recruitment Message (With correct invite)
# $RULES - Display Rules
# $TITLES - Promotion Information
# 
# CONTESTS
# $CONTEST - Current Contest Details
# $INIT_CONTEST - Reset Any Information Regarding Random Number Generator
# $LIFT - Needs Reward Code Then It will Return Common, Uncommon or Rare
# 
# USER DATABASE
# $IGN - Sets In-Game-Name In Database
# $PLANET - Sets Furthest Planet
# $QUEST - Sets Current Quest
# $FRAME - Sets Most Used Frame
# $PRIORITY - Sets Largest Priority At The Moment
# $ADDSYNDICATE - Adds Syndicate Role For Others To Mention In Discord Chat
# $REMOVESYNDICATE - Remove Syndicale Role From Your Account
# $FIND - Lookup By IGN
# $FINDIGN - Loopup By Username
# $MYSELF - Display Your Own Information
# $ALL - Lists Everyone Along With Their IGN
# 
# WARFRAME DATA
# $EARTH - Displays Current Day/Night Status At Earth/Cetus
# $DARVO - Current Darvo Weapon Deal
# $TRADER or When Baro? - Displays Information Regarding The Void Trader
# $ENDLESS - Current Endless Fissures
# $FISSURES - All Current Fissures
# 
# ADMIN
# $KILL - Disconnect Discordis (Requires Secret Key)
# $CLEAR - Clears Lines Of Messages (Requires Secret Key)


    

    if message.content.upper() == '$INFO':
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name="Senua Black", value=missionStatement)
        await client.send_message(message.channel, embed=embed)
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/priNXCM.jpg')
        embed.add_field(name="Discordis", value=botInfo)
        await client.send_message(message.channel, embed=embed)
    else:
        pass


    if message.content.upper() == '$BOT':
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/priNXCM.jpg')
        embed.add_field(name="Discordis Bot Commands", value=botInfo)
        await client.send_message(message.channel, embed=embed)
    else:
        pass


    if message.content.upper() == '$RECRUIT':
        await client.send_message(message.channel, recruitMessage)
        await client.send_message(message.channel, "\n\nDiscord Invite:   https://discord.gg/YZMXwtX")
    else:
        pass


    if message.content.upper() == '$RULES':
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name="Guidelines For Senua Black", value=rulesOne)
        await client.send_message(message.channel, embed=embed)
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name="Guidelines For Senua Black", value=rulesTwo)
        await client.send_message(message.channel, embed=embed)
    else:
        pass


    if message.content.upper() == '$TITLES':
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/priNXCM.jpg')
        embed.add_field(name="Titles", value=titles)
        await client.send_message(message.channel, embed=embed)
    else:
        pass
    

    if message.content.upper() == '$CONTEST':
        await client.send_message(message.channel, contest)
    else:
        pass


    if message.content.upper() == '$INIT_CONTEST':
        await client.send_message(message.channel, "To initiate all pointers and keys enter Contest Key")
        contestKey = await client.wait_for_message(author=message.author)
        if str(contestKey.content) == redis_server.get('CONTEST_KEY').decode('utf-8'):
            redis_server.set('REWARD_ALL', True)
            redis_server.set('REWARD_ONE', False)
            redis_server.set('WINNING_KEY', '10001110101')
            await client.send_message(message.channel, "Contest Initialized")
        else:
            await client.send_message(message.channel, "Wrong Contest Key")
    else:
        pass

    if message.content.upper() == '$LIFT':
        await client.send_message(message.channel, "Enter your Contest Key")
        contestKey = await client.wait_for_message(author=message.author)
        contestKeyInt = str(contestKey.content)
        winningKey = redis_server.get('WINNING_KEY').decode('utf-8')
        everyonesKey = redis_server.get('EVERYONES_KEY').decode('utf-8')
        bothKeys = (winningKey, everyonesKey)
        if contestKeyInt not in bothKeys:
            await client.send_message(message.channel, "The contest is over and this key has been used.  Check your inbox for details about your chosen Reward.  If you received nothing then contact @withinmyself to rectify the situation.")
        else:
            if winningKey == '00001111':
                await client.send_message(message.channel, "The contest is over and this key has been used.  Check your inbox for details about your chosen Reward.  If you received nothing then contact @withinmyself to rectify the situation.")
            else:
                pass
            if contestKeyInt == winningKey:
                redis_server.set('WINNING_KEY', '00001111')
                winner = random.randint(1, 49)

                await client.send_message(message.channel, "Compiling Results...")
                time.sleep(2)
                await client.send_message(message.channel, "...")
                time.sleep(3)
                await client.send_message(message.channel, "..")
                time.sleep(3)
                await client.send_message(message.channel, ".")
                time.sleep(4)
                if winner >= 1 and winner <= 25:
                    await client.send_message(message.channel, "Common Reward!  You lucky luck luck boy!!")
                    time.sleep(2)
                    await client.send_message(message.author, "Message the word FLIP to @withinmyself  along with your chosen Reward from either RARE, UNCOMMON or COMMON")
                if winner >= 26 and winner <= 40:
                    await client.send_message(message.channel, "Uncommon Reward!  WTF Man!!!  You are one lucky SOB!!")
                    time.sleep(2)
                    await client.send_message(message.author, "Message the word RAS to @withinmyself along with your chosen Reward from either RARE,  UCOMMON or COMON")
                if winner >= 41 and winner <= 50:
                    await client.send_message(message.channel, "RARE Reward!  You...Have GOT...To be kidding me!!!")
                    time.sleep(2)
                    await client.send_message(message.author, "Message the word AND to @withinmyself along with your chosen Reward from either RARE, UNCOMMON or COMMON")
            else:
                pass
  
    else:
        pass
    

    if message.content.upper() == '$IGN':
        await client.send_message(message.channel, "Type in your correct IGN and hit [ENTER].")
        ign = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(ign.author)).first()
        

        if current == None:          # Is user in the database?

            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            session.add(current)
            session.commit()
        else:
            current.ign = str(ign.content)
            session.add(current)
            session.commit()
        await client.send_message(message.channel, success.format(ign.content))
    else:
        pass


    if message.content.upper() == '$PLANET':
        await client.send_message(message.channel, "Please type the furthest Planet you've unlocked and hit enter.")
        planet = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(planet.author)).first() 

        if current == None:

            await client.send_message(message.channel, addMember)
            ign = await client.wait_for_message(author=message.author)
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            await client.send_message(message.channel, success.format(ign.content))
        else:
            pass
        
        current.planet = str(planet.content)

        session.add(current)
        session.commit()
        await client.send_message(message.channel, "{0} has been saved as the furthest Planet you've unlocked.  Use $MYSELF to see everything The Database knows about you.".format(current.planet))
        if debug == True:
            print("Planet Added - {}".format(current.planet))
    else:
	    pass

    if message.content.upper() == '$FRAME':
        await client.send_message(message.channel, "What Warframe do you use the most?")
        frame = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(frame.author)).first() 

        if current == None:

            await client.send_message(message.channel, addMember)
            ign = await client.wait_for_message(author=message.author)
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            await client.send_message(message.channel, success.format(ign.content))
        else:
            pass
        
        current.syndicate = str(frame.content)

        session.add(current)
        session.commit()
        await client.send_message(message.channel, "{0} has been saved as your most used Warframe.  Use $MYSELF to see everything The Database knows about you.".format(current.syndicate))
        if debug == True:
            print("Frame Added - {}".format(current.syndicate))
    else:
	    pass


    if message.content.upper() == '$QUEST':
        await client.send_message(message.channel, "Please type the name of your current Quest and hit enter")
        quest = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(quest.author)).first() 

        if current == None:

            await client.send_message(message.channel, addMember)
            ign = await client.wait_for_message(author=message.author)

            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')

            await client.send_message(message.channel,success.format(ign.content))
        else:
            pass
        
        current.quest = str(quest.content)

        session.add(current)
        session.commit()
        await client.send_message(message.channel, "{0} has been saved as your current Quest.    Use $MYSELF to see everything The Database knows about you.".format(current.quest))

        if debug == True:
            print("Quest Added - {}".format(current.quest))
    else:
	    pass
    
    if message.content.upper() == '$PRIORITY':
        await client.send_message(message.channel, "What's at the top of your Warframe Bucketlist?")
        priority = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(priority.author)).first() 
        
        if current == None:
            await client.send_message(message.channel, addMember)
            ign = await client.wait_for_message(author=message.author)
            # Initialize new Member Object
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            await client.send_message(message.channel, success.format(ign.content))
        else:
            pass
        
        current.priority = str(priority.content)

        session.add(current)
        session.commit()
        await client.send_message(message.channel, "{0} has been set as your top priority.   Use $MYSELF to see everything The Database knows about you.".format(current.priority))

        if debug == True:
            print("Priority Added Succesfully - {}".format(current.priority))
    else:
	    pass


    if message.content.upper() == '$ADDSYNDICATE':
        await client.send_message(message.channel, syndicateRole)
        add_syndicate = await client.wait_for_message(author=message.author)
        syndicate_str = str(add_syndicate.content)
        if syndicate_str.upper() in syndicates:
            for server in client.servers:
                for role in server.roles:
                    if role.name.upper() == syndicate_str.upper():
                        await client.add_roles(message.author, role)
                        await client.send_message(message.channel, success)
                        if debug == True:
                            print("Added Syndicate - {}".format(role.name))
                        break
                    else:
                        continue
        else:
            await client.send_message(message.channel, tryAgain )
    else:
        pass


    if message.content.upper() == '$REMOVESYNDICATE':
        await client.send_message(message.channel,  syndicateRole)
        syn_gone = await client.wait_for_message(author = message.author)
        synGone_str = str(syn_gone.content)
        if synGone_str.upper() in syndicates:
            for server in client.servers:
                for role in server.roles:
                    if role.name.upper() == synGone_str.upper():
                        await client.remove_roles(message.author, role)
                        await client.send_message(message.channel, success)
                        if debug == True:
                            print("Removed Syndicate - {}".format(role.name))
                        break
                    else:
                        continue
        else:
            await client.send_message(message.channel,  tryAgain)

        
    if message.content.upper() == '$FIND':
        await client.send_message(message.channel, "Type the IGN of the member you'd like to look up and hit [ENTER]")
        current_ign = await client.wait_for_message(author=message.author)
        ign_str = str(current_ign.content)
        session = Session()
        self_object = session.query(Member).filter_by(ign=ign_str).first()
        if self_object != None:
            embed = discord.Embed (title = 'Warframe Status',
	        description = 'Database Information',
	        colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.set_author(name=self_object.ign, icon_url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name="Furthest Planet", value=self_object.planet)
            embed.add_field(name="Current Quest", value=self_object.quest)
            embed.add_field(name="Main Frame", value=self_object.syndicate)
            embed.add_field(name="Top Priority", value=self_object.priority, inline=False)
            await client.send_message(message.channel, embed=embed)
        else:
            await client.send_message(message.channel, "There is no user in The Database that goes by that IGN.")
    else:
        pass

    if message.content.upper() == '$FINDIGN':
        await client.send_message(message.channel, "Type the first 2-5 characters of the Discord username for the member who's IGN you'd like to find")
        username = await client.wait_for_message(author=message.author)
        username_str = str(username.content)
        session = Session()
        usersObject = session.query(Member).all()
        for user in usersObject:
            if username_str in user.user:
                await client.send_message(message.channel, "**User: {0}** is known as **{1}** in Warframe".format(user.user, user.ign))
            else:
                continue
        await client.send_message(message.channel, "Search complete.  If nothing was found, try omitting any characters that aren't letters or numbers or you can just use $ALL to see everyone.")


    if message.content.upper() == '$MYSELF':
        userStr = str(message.author)
        session = Session()
        self_object = session.query(Member).filter_by(user=userStr).first()
        if self_object == None:
            await client.send_message(message.channel, addMember)
            ign = await client.wait_for_message(author=message.author)
            # Initialize new Member Object
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            await client.send_message(message.channel, success.format(ign.content))
        else:
            pass
        embed = discord.Embed (title = 'Warframe Status',
	    description = 'Database Information',
	    colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.set_author(name=self_object.ign, icon_url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name="Furthest Planet", value=self_object.planet)
        embed.add_field(name="Current Quest", value=self_object.quest)
        embed.add_field(name="Main Frame", value=self_object.syndicate)
        embed.add_field(name="Top Priority", value=self_object.priority, inline=False)
        await client.send_message(message.channel, embed=embed)
    else:
        pass


    if message.content.upper() == '$ALL':
        session = Session()
        allMembers = session.query(Member).all()
        for member in allMembers:
            if member.quest != 'DEBUG':
                await client.send_message(message.channel, "**User: {0}**   **IGN: {1}**  **Priority: {2}**".format(
                                                                                                        member.user, member.ign, member.priority))

    if message.content.upper() == "$EARTH":
        req = Request('https://api.warframestat.us/pc/cetusCycle', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        if data['isDay'] == True:
            await client.send_message(message.channel, "It Is Currently Day Time On Earth With {} Left Until Night".format(data['timeLeft']))
        if data['isDay'] == False:
            await client.send_message(message.channel, "It Is Currently Night Time On Earth With {} Left Until Morning".format(data['timeLeft']))    
    
    #  create string to search multiple words in so we can use 'when baro' or 'when the hell is baro gonna get here'
    baroMsg = str(message.content.upper())
    if ("WHEN" in baroMsg and "BARO" in baroMsg) or baroMsg == "$TRADER":
        req = Request('https://api.warframestat.us/pc/voidTrader', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        if data['active'] == False:
            await client.send_message(message.channel, "Baro Ki`Teer will be arriving at {0} in {1}.".format(data['location'], data['startString']))
        else:
            pass
        if data['active'] == True:
            inventory = data['inventory']

            # Return inventory as formated text to the channel.
            await client.send_message(message.channel, "The Void Trader has already arrived!!  You'll find him at {0}.  He will be leaving in {1}.  Check out what he brought!!\n\n".format(data['location'], data['endString']))
            for stuff in inventory:
                await client.send_message(message.channel, "**{0}**  *Ducats:* __{1}__  *Credits:* __{2}__".format(stuff['item'], stuff['ducats'], stuff['credits']))
        else:
            pass
    else:
        pass

    if message.content.upper() == '$ENDLESS':
        req = Request('https://api.warframestat.us/pc/fissures', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        missionTypes = ('Defense', 'Survival', 'Interception', 'Excavation')
        x = 0
        for mission in data:
            if mission['missionType'] in missionTypes:
                await client.send_message(message.channel, "**{0}**~~//~~**{1}**  *{2}*  __{3}__".format(
                                                                    mission['tier'], mission['missionType'], mission['node'], mission['eta']))
                x = x + 1
                continue
            else:
                continue
        if debug == True:
            print("{0}".format(x))
        if x == 0:
            await client.send_message(message.channel, "No Endless Fissure Missions available at this time.")
        else:
            pass


    if message.content.upper() == '$FISSURES':
        req = Request('https://api.warframestat.us/pc/fissures', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        for mission in data:
            await client.send_message(message.channel, "**{0}**~~//~~**{1}**  *{2}*  __{3}__".format(
                                                                mission['tier'], mission['missionType'], mission['node'], mission['eta']))
    else:
        pass
    

    if message.content.upper() == '$DARVO':
        req = Request('https://api.warframestat.us/pc/dailyDeals', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        dataPack = json.loads(webpage)
        for data in dataPack:
            totalLeft = int(data['total'] - data['sold'])
            if totalLeft == 0:
                await client.send_message(message.channel, "Darvo has sold out.  {0} is no longer available at a lower price.".format(data['item']))
            else:
                await client.send_message(message.channel, "**{0}**   *Original Price:* **{1}**   *Sale Price:* **{2}**   **{3} ** *Remaining*   __{4}__".format(
                                                                    data['item'], data['originalPrice'], data['salePrice'], totalLeft, data['eta']))
    else:
        pass
    







    # Everything below is used for Administrative purposes
    # Admin functions called inside Discord require a Secret Key to activate
    # The Secret Key is stored in Redis
    
    if message.content.upper() == '$KILL':
        await client.send_message(message.channel, "Admin Kill Command")
        await client.send_message(message.channel, "Type Secret Key")
        secretKey = await client.wait_for_message(author = message.author)
        if str(secretKey.content) == redis_server.get('SECRET_KEY').decode('utf-8'):
            await client.send_message(message.channel, "Key Accepted.  Discordis Killed")
            await client.purge_from(message.channel, limit=3)
            await client.logout()
        else:
            await client.send_message(message.channel, "Wrong Key.   Start Over.")
    else:
        pass

    if message.content.upper() == '$CLEAR':
        await client.send_message(message.channel, "Admin Clear Command")
        await client.send_message(message.channel, "Type Secret Key")
        secretKey = await client.wait_for_message(author = message.author)
        if str(secretKey.content) == redis_server.get('SECRET_KEY').decode('utf-8'):
            await client.send_message(message.channel, "Key Accepted. How Many Lines Shall I Clear?")
            lines = await client.wait_for_message(author = message.author)
            intLines = int(lines.content)
            await client.purge_from(message.channel, limit=intLines)      
        else:
            await client.send_message(message.channel, "Wrong Key. Start Over.")
    else:
        pass


# Use Redis to store Discord Token.
client.run(redis_server.get('SENUA_TOKEN').decode('utf-8'))