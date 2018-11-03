import asyncio
import time
import redis
import json

import discord
from discord.ext.commands import Bot
from discord.ext import commands
from urllib.request import Request, urlopen

from senua_db import Member, Session, Base, engine
from strings import botInfo, welcome, ignAdd, senuaMission, addMember, syndicateRole, syndicates, tryAgain, success




Client = discord.Client()
client = commands.Bot(command_prefix = "!")
redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)

# Turn on various print statements that verify functions and database access
debug=True

# Embed One.  $INFO
botEmbed = discord.Embed(colour = discord.Colour.red())
botEmbed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
botEmbed.add_field(name="Senua Black", value=senuaMission)

# Embed Two. $HELP
botEmbedTwo = discord.Embed(colour = discord.Colour.red())
botEmbedTwo.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
botEmbedTwo.add_field(name="Senua Black", value=botInfo)


# If 'Discordis Bot Ready' prints to terminal then the bot has successfully started in Discord
@client.event
async def on_ready():
    print("Discordis Bot Ready")
    redis_server.set('ARRIVAL_COUNT', 0)
@client.event
async def on_member_join(member):
    # Assign New Arrival role to new member.
    redis_server.incr('ARRIVAL_COUNT')
    x = redis_server.get('ARRIVAL_COUNT')
    for server in client.servers:
        for role in server.roles:
            if role.name == 'New Arrival':
                await client.add_roles(member, role)
                break
            else:
                continue
        break
    # Explain that they must provide their IGN to continue.
    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'welcome':
                await client.purge_from(channel, limit=100)
                redis_server.set('WELCOME{0}'.format(x), 'welcome_{0:{1}}'.format(member.name, len(member.name) - 4))
                redis_server.set('USER{0}'.format(x), '{0:{1}}'.format(member.name, len(member.name) - 4))
                await client.edit_channel(channel, name=redis_server.get('WELCOME{0}'.format(x)).decode('utf-8'))

                await client.send_message(channel,welcome.format(
                                        member.name, len(member.name) - 4))
                break
            else:
                continue
        break

    ign = await client.wait_for_message(author=member)
    # Ask user to try again if no response is given.
    if ign.content == None:
        await client.send_message(member, ignAdd)
        ign = await client.wait_for_message(author=message.name)

        # If the user still doesn't respond he/she is kicked but not banned. 
        if ign.content == None:
            kick(member)
        else:
            pass
    else:
        pass
    
    await client.delete_channel(ign.channel)
    # Save new member into SQL using SQLAlchemy
    newMember = Member(user=str(ign.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
    session = Session()
    session.add(newMember)
    session.commit()
    
    # Send welcome message to main channel for everyone to see that a new member has joined and is now in the database.
    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'warframe':
                await client.send_message(channel, "Please welcome {0} to Senua Black.  They are known as {1} in Warframe.  Remember to use $INFO for Helpful Information or $HELP for a list of all our cool Bot commands.".format(
                                                                                                                                                    redis_server.get('USER{0}'.format(x)).decode('utf-8'),  str(newMember.ign)))
                break
            else:
                continue
        break

	# Now that we have the members IGN we automatically assign the role Initiate so they can access the main channel.
    for server in client.servers:
        for role in server.roles:
            if role.name == 'Initiates':
                await client.replace_roles(member, role)
                # await client.delete_channel(member.channel)
                break
            else:
                continue
        break
    

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

@client.event
async def on_message(message):

    # Test case for monitoring separate individuals perpetrating more than one offense
    destinyTwo = str(message.content.upper())
    if 'DESTINY' in destinyTwo and 'SUCKS' not in destinyTwo:
        if redis_server.get('{0}_no'.format(str(message.author))) == None:
            redis_server.set('{0}_no'.format(str(message.author)), 0)
        else:
            pass
        violations = redis_server.incr('{0}_no'.format(str(message.author)))
        if violations == 1:
            await client.send_message(message.channel, "You have violated one of Senua Blacks policies by speaking of this subject.  This is your first offense.")
        if violations == 2:
            await client.send_message(message.channel, "This is the second time you have chosen to speak that which is unspeakable.  Let us never speak of this again.")
        if violations == 3:
            await client.send_message(message.channel, "Thrice now you have stained this screen with blasphemous nonsense! No more I say! A penance will be wrought if your actions continue!")
        if violations == 4:
            await client.send_message(message.channel, "You leave me no choice but to retaliate!  I hope you're ready for this!")
            await client.send_message(message.channel, "**Destiny sucks!**")
        if violations >= 5:
            await client.send_message(message.channel, "**Destiny sucks!**")
    else:
        pass
    
    # After repeated violations we start sending a private message to the user every time they post anything at all
    if  redis_server.get('{0}_no'.format(str(message.author))) != None:
        if  int(str(redis_server.get('{0}_no'.format(str(message.author))).decode('utf-8'))) >= 4:
            await client.send_message(message.author, "**Destiny sucks!**")

    # Resets violation counter to stop retaliation
    if message.content.upper() == '$INIT':
        redis_server.set('{0}_no'.format(str(message.author)), 0)
    else:
        pass
    
    # Display Senua Black Information
    if message.content.upper() == '$INFO':
        await client.send_message(message.channel, embed=botEmbed)
    else:
        pass

    # Display Bot commands.
    if message.content.upper() == '$HELP':
        await client.send_message(message.channel, embed=botEmbedTwo)
    else:
        pass

    # Every command that allows a user to add/change information to the database
    # automatically checks to see if that user has even been added.  If they haven't then it will ask
    # for their IGN and it will set the rest of the values to 'Not Set'.  Whatever piece of information
    # the user was trying to add will continue like normal after that is done.

    # Change/Add your in-game-name
    if message.content.upper() == '$IGN':
        await client.send_message(message.channel, "Type in your correct IGN and hit [ENTER].")
        ign = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(ign.author)).first()
        
        # Is User in Database?  We don't ask the user for their IGN if they are not because they have already given it to us
        if current == None:
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            await client.send_message(message.channel, success.format(ign.content))
        else:
            current.ign = str(ign.content)

            # Commit to The Database
            session.add(current)
            session.commit()
            await client.send_message(message.channel, success.format(ign.content))
    else:
        pass

    # Add Planet
    if message.content.upper() == '$PLANET':
        await client.send_message(message.channel, "Please type the furthest Planet you've unlocked and hit enter.")
        planet = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(planet.author)).first() 

        # Check if User is in Database
        if current == None:

            # If not then ask the User for their IGN
            await client.send_message(message.channel, addMember)
            ign = await client.wait_for_message(author=message.author)
            # Initialize new Member Object
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            # Send success message to channel
            await client.send_message(message.channel, success.format(ign.content))
        else:
            pass
        
        # Continue adding the given Planet
        current.planet = str(planet.content)

        # Commit to The Database
        session.add(current)
        session.commit()
        await client.send_message(message.channel, "{0} has been saved as the furthest Planet you've unlocked.  Use $MYSELF to see everything The Database knows about you.".format(current.planet))
        if debug == True:
            print("Planet Added - {}".format(current.planet))
    else:
	    pass

    # Add Quest
    if message.content.upper() == '$QUEST':
        await client.send_message(message.channel, "Please type the name of your current Quest and hit enter")
        quest = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(quest.author)).first() 

        # Check if User is in Database
        if current == None:

            # Ask for IGN if not 
            await client.send_message(message.channel, addMember)
            ign = await client.wait_for_message(author=message.author)

            # Initialize new Member Object with IGN
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')

            # Send success message to channel
            await client.send_message(message.channel,success.format(ign.content))
        else:
            pass
        
        # Continue adding the given Quest
        current.quest = str(quest.content)

        # Commit to The Database
        session.add(current)
        session.commit()
        await client.send_message(message.channel, "{0} has been saved as your current Quest.    Use $MYSELF to see everything The Database knows about you.".format(current.quest))

        if debug == True:
            print("Quest Added - {}".format(current.quest))
    else:
	    pass
    
    # Add Priority.
    if message.content.upper() == '$PRIORITY':
        await client.send_message(message.channel, "What's at the top of your Warframe Bucketlist?")
        priority = await client.wait_for_message(author=message.author)
        session = Session()
        current = session.query(Member).filter_by(user=str(priority.author)).first() 
        
        # Check if User is in Database
        if current == None:
            await client.send_message(message.channel, addMember)
            ign = await client.wait_for_message(author=message.author)
            # Initialize new Member Object
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            await client.send_message(message.channel, success.format(ign.content))
        else:
            pass
        
        # Continue adding Priority
        current.priority = str(priority.content)

        # Commit to The Database
        session.add(current)
        session.commit()
        await client.send_message(message.channel, "{0} has been set as your top priority.   Use $MYSELF to see everything The Database knows about you.".format(current.priority))

        if debug == True:
            print("Priority Added Succesfully - {}".format(current.priority))
    else:
	    pass

    # The following Syndicate commands do not interact with The Database.
    # They add a new role to the User.  These roles are already created.
    # All the syndicate names are saved in syndicates which is imported from strings.py.
    # If the User does not type in an exact match for one of the syndicates in that string
    # it will tell them to start over.  None of the Bot commands are case sensative as all 
    # messages are converted to uppercase before being checked against uppercase options.

    # Add Syndicate Role
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

    # Remove Syndicate role.
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

        
    # Search Database with IGN then display that Users information
    if message.content.upper() == '$FIND':
        await client.send_message(message.channel, "Type the IGN of the member you'd like to look up and hit [ENTER]")
        current_ign = await client.wait_for_message(author=message.author)
        ign_str = str(current_ign.content)
        session = Session()
        self_object = session.query(Member).filter_by(ign=ign_str).first()
        embed = discord.Embed (title = 'Warframe Status',
	    description = 'Database Information For Members Of Senua Black',
	    colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.set_author(name=self_object.ign, icon_url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name="Furthest Planet", value=self_object.planet)
        embed.add_field(name="Current Quest", value=self_object.quest)
        embed.add_field(name="Biggest Priority", value=self_object.priority, inline=False)
        await client.send_message(message.channel, embed=embed)
    else:
        pass

    # Returns Database information on self
    if message.content.upper() == '$MYSELF':
        userStr = str(message.author)
        session = Session()
        self_object = session.query(Member).filter_by(user=userStr).first()
        embed = discord.Embed (title = 'Warframe Status',
	    description = 'Database Information For Members Of Senua Black',
	    colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.set_author(name=self_object.ign, icon_url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name="Furthest Planet", value=self_object.planet)
        embed.add_field(name="Current Quest", value=self_object.quest)
        embed.add_field(name="Biggest Priority", value=self_object.priority, inline=False)
        await client.send_message(message.channel, embed=embed)
    else:
        pass

    # Day/Night Information for Cetus/Earth in Warframe.
    if message.content.upper() == "$EARTH":
        req = Request('https://api.warframestat.us/pc/cetusCycle', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        if data['isDay'] == True:
            await client.send_message(message.channel, "It Is Currently Day Time On Earth With {} Left Until Night".format(data['timeLeft']))
        if data['isDay'] == False:
            await client.send_message(channel, "It Is Currently Night Time On Earth With {} Left Until Morning".format(data['timeLeft']))    
    
    # Return information on The Void Trader in Warframe.
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
    
    # Check if any Endless Fissures are available and display information
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

    # Display ALL Fissure Missions currently available
    if message.content.upper() == '$FISSURES':
        req = Request('https://api.warframestat.us/pc/fissures', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        for mission in data:
            await client.send_message(message.channel, "**{0}**~~//~~**{1}**  *{2}*  __{3}__".format(
                                                                mission['tier'], mission['missionType'], mission['node'], mission['eta']))
    else:
        pass
    
    # Display Darvos current deal
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
    







    # Everything below this comment is used for Administrative purposes
    # Admin functions called inside Discord require a Secret Key to activate
    # The Secret Key is stored in Redis

    if message.content.upper() == '$KILL':
        await client.send_message(message.channel, "Admin Kill Command")
        await client.send_message(message.channel, "Type Secret Key")
        secretKey = await client.wait_for_message(author = message.author)
        if str(secretKey.content) == redis_server.get('SECRET_KEY').decode('utf-8'):
            await client.send_message(message.channel, "Key Accepted.  Discordis Killed")
            await client.logout()
        else:
            await client.send_message(message.channel, "Wrong Key.   Start Over.")
    else:
        pass


# Use Redis to store Discord Token.
client.run(redis_server.get('SENUA_TOKEN').decode('utf-8'))