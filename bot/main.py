import asyncio
import time
import redis
import json
import random
import schedule

import discord
from discord.ext.commands import Bot
from discord.ext import commands
from urllib.request import Request, urlopen

from senua_db import Member, Session, Base, Clan, engine
from strings import botInfo, welcome, ignAdd, \
    addMember, syndicateRole, syndicates, tryAgain, success, \
    recruitMessage, rulesOne, rulesTwo, titles, missionStatement, \
    welcomeMessage, contest, rivenList, policies, policies2


Client = discord.Client()
client = commands.Bot(command_prefix = "!")
redis_server = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)


# Verify functionality  
debug=True


@client.event
async def on_ready():
    print("Discordis Bot Ready")
    redis_server.set('ARRIVAL_COUNT', 0)  # Track users who are currently joining  
    redis_server.set('MOTD_TIMER', 0) # For displaying MOTD a certain amount of times


@client.event
async def on_member_join(member):
#    Triggered when a new member joins.  
    for server in client.servers:
        for role in server.roles:
            if role.name == 'Visitor':
                await client.add_roles(member, role)
                break
            else:
                continue

    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
    embed.add_field(name='Thanks For Visiting!!', value='Welcome to Senua Black Discord!  This is our main text channel.  You also have access to our bot channel and our main voice channel.\n\nIf you have any questions or just want to say hi then start typing.  You can type $WARFRAME to see how Discordis interacts with the game.\n\nIf you decide that you want to join our Clan, just let one of the Warlords or Generals know and they will get an invite sent out to you.\n\nAfter you have joined, you will be able to access the rest of our Discord channels which include Clan Builds, Fashion, Theories, Trade, Guides and much more!')
    await client.send_message(member, embed=embed)
    await client.send_message(member, '{0}\n{1}'.format(policies, policies2))
    for server in client.servers:
        for channel in server.channels:
            if channel.name == 'main':
                embed = discord.Embed(colour = discord.Colour.red())
                embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
                embed.add_field(name='Welcome!!', value='Please welcome {0:{1}}!  They are visiting Senua Black Discord for the first time.  If they have any questions please try your best to answer.'.format(member.name, len(member.name)-4))
                await client.send_message(channel, embed=embed)




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
    def redis_motd():
        redis_server.set('MOTD', True)
    schedule.every().day.at("19:30").do(redis_motd)
    schedule.run_pending()
    time.sleep(1)

    if redis_server.get('MOTD') == b'True':
        redis_server.set('MOTD', False)
        for server in client.servers:
            for channel in server.channels:
                if channel.name == 'main':
                    session = Session()
                    clan = session.query(Clan).filter_by(clan_name='Senua Black').first()
                    embed = discord.Embed(colour = discord.Colour.red())
                    embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
                    embed.add_field(name='Senua Black MOTD', value=clan.clan_priority)
                    embed.add_field(name='Current Research', value='We are currently researching {0}'.format(clan.clan_research), inline=False)
                    await client.send_message(channel, embed=embed)
    if message.content.upper() == '$POLICIES':
        await client.send_message(message.author, 'Updated Senua Black Policies - 02/25/2019\n\n{0}\n{1}'.format(policies, policies2))
    else:
        pass

    if message.content.upper() == '$REGISTER':
        await client.send_message(message.author, 'Which are you?\n\n1. Leader 2. Initiate\n\nType 1 or 2 and hit [ENTER]')
        which = await client.wait_for_message(author=message.author)
        if str(which.content) != '1' and str(which.content) != '2':
            await client.sent_message(message.author, 'Invalid Response - Restart Registration Process')
        elif str(which.content) == '1':
            await client.send_message(message.author, 'This Area Is For Leaders Only!\n\nPassword?')
            passWord = await client.wait_for_message(author=message.author)
            if str(passWord.content) != '4269':
                await client.send_message(message.author, 'Wrong Password! Begin Registration From The Beginning')
            else:
                await client.send_message(message.author, 'Password Accepted\n\nEnter The Discord Username Of The Member You Wish To Register')
                userName = await client.wait_for_message(author=message.author)
                await client.send_message(message.author, 'Where Does This Member Belong?\n\n1. Clan 2. Alliance\n\nType 1 or 2 and hit [ENTER]')
                clanOrAlliance = await client.wait_for_message(author=message.author)
                if str(clanOrAlliance.content) == '1':
                    for server in client.servers:
                        for member in server.members:
                            if str(userName.content).upper() in member.name.upper():
                                redis_server.set('MEMBER', '{0}'.format(member.name))
                                for server in client.servers:
                                    for role in server.roles:
                                        if role.name == 'Soldiers':
                                            await client.replace_roles(member, role)
                                            break
                                        else:
                                            continue
                            else:
                                continue
                    await client.send_message(message.author, 'What Is The In-Game-Name For This User?')
                    ign = await client.wait_for_message(author=message.author)
                    session = Session()
                    current = Member(user=str(redis_server.get('MEMBER').decode('utf-8')), ign = str(ign.content), planet='Not Set', priority='Not Set', syndicate='Not Set')
                    session.add(current)
                    session.commit()
                    await client.send_message(message.author, 'You Have Successfully Registered A New Member')
                elif str(clanOrAlliance.content) == '2':
                    for server in client.servers:
                        for member in server.members:
                            if str(userName.content).upper() in member.name.upper():
                                redis_server.set('MEMBER', '{0}'.format(member.name))
                                for server in client.servers:
                                    for role in server.roles:
                                        if role.name == 'Alliance':
                                            await client.replace_roles(member, role)
                                            break
                                        else:
                                            continue
                            else:
                                continue
                    await client.send_message(message.author, 'What Is The In-Game-Name For This User?')
                    ign = await client.wait_for_message(author=message.author)
                    session = Session()
                    current = Member(user=str(redis_server.get('MEMBER').decode('utf-8')), ign = str(ign.content), planet='Not Set', priority='Not Set', syndicate='Not Set')
                    session.add(current)
                    session.commit()
                    await client.send_message(message.author, 'You Have Successfully Registered A New Member')
                elif str(clanOrAlliance.content) != '1' and str(clanOrAlliance.content) != '2':
                    await client.send_message(message.author, 'Incorrect Selection - Please Restart Registration Process')
                else:
                    pass
        elif str(which.content) == '2':
            await client.send_message(message.author, 'Which Are You Joining?\n\n1. Clan 2. Alliance\n\nType 1 or 2 And Hit [ENTER]')
            clanOrAlliance = await client.wait_for_message(author=message.author)
            if str(clanOrAlliance.content) != '1' and str(clanOrAlliance.content) != '2':
                await client.send_message(message.author, 'Invalid Response - Restart Registration Process')
            elif str(clanOrAlliance.content) == '1':
                for server in client.servers:
                    for role in server.roles:
                        if role.name == 'Soldiers':
                            await client.replace_roles(message.author, role)
                            break
                        else:
                            continue
                await client.send_message(message.author, 'What Is Your In-Game-Name?')
                ign = await client.wait_for_message(author=message.author)
                session = Session()
                current = Member(user=str(ign.author), ign = str(ign.content), planet='Not Set', priority='Not Set', syndicate='Not Set')
                session.add(current)
                session.commit()
                await client.send_message(message.author, 'You Have Successfully Completed Registratior')
            elif str(clanOrAlliance.content) == '2':
                for server in client.servers:
                    for role in server.roles:
                        if role.name == 'Alliance':
                            await client.replace_roles(message.author, role)
                            break
                        else:
                            continue
                await client.send_message(message.author, 'What Is Your In-Game-Name?')
                ign = await client.wait_for_message(author=message.author)
                session = Session()
                current = Member(user=str(ign.author), ign = str(ign.content), planet='Not Set', priority='Not Set', syndicate='Not Set')
                session.add(current)
                session.commit()
                await client.send_message(message.author, 'You Successfully Completed Registratior')
            else:
                pass
    else:
        pass

    if message.content.upper() == '$BLASTMOTD':
        for server in client.servers:
            for channel in server.channels:
                if channel.name == 'main':
                    session = Session()
                    clan = session.query(Clan).filter_by(clan_name='Senua Black').first()
                    embed = discord.Embed(colour = discord.Colour.red())
                    embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
                    embed.add_field(name='Senua Black MOTD', value=clan.clan_priority)
                    embed.add_field(name='Current Research', value='We are currently researching {0}'.format(clan.clan_research), inline=False)
                    await client.send_message(channel, embed=embed)
    else:
        pass

    if message.content.upper() == '$INFO':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/priNXCM.jpg')
        embed.add_field(name="Discordis", value=botInfo)
        await client.send_message(message.channel, embed=embed)
    else:
        pass

    if message.content.upper() == '$WARFRAME':
        await client.send_message(message.channel, '$EARTH - Displays Current Day/Night Status At Earth/Cetus\n$DARVO - Current Darvo Weapon Deal\n$TRADER - Displays Information Regarding The Void Trader\n$ENDLESS - Current Endless Fissures\n$FISSURES - All Current Fissures\n$FORTUNA - Displays Cold/Warm Cycle at Orb Vallis')

    if message.content.upper() == '$SECRETS':
        redis_server.set('SECRETS', 'NO')
        req = Request('https://api.warframestat.us/pc/syndicateMissions', headers={'user-agent':'mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        x = 0
        for mission in data:
            if mission['syndicate'] == 'Ostrons':
                for job in mission['jobs']:
                    for reward in job['rewardPool']:
                        if reward.upper() == 'AUGUR SECRETS':
                            await client.send_message(message.channel, 'Augur Secrets is currently being offered as a reward!')
                            x = 0
                            break
                        else:
                            continue
                    x += 1
                if x == 5:
                    await client.send_message(message.channel, 'Augur Secrets is not currently being offered as a reward.')
                else:
                    pass
            else:
                continue

    else:
        pass

    if message.content.upper() == '$VICE':
        redis_server.set('VICE', 'NO')
        req = Request('https://api.warframestat.us/pc/syndicateMissions', headers={'user-agent':'mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        x = 0
        for mission in data:
            if mission['syndicate'] == 'Ostrons':
                for job in mission['jobs']:
                    for reward in job['rewardPool']:
                        if reward.upper() == 'GLADIATOR VICE':
                            await client.send_message(message.channel, 'Gladiator Vice is currently being offered as a reward!')
                            x = 0
                            break
                        else:
                            continue
                    x += 1
                if x == 5:
                    await client.send_message(message.channel, 'Gladiator Vice is not currently being offered as a reward.')
                else:
                    pass
            else:
                continue

    else:
        pass





    if message.content.upper() == '$BOT':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/priNXCM.jpg')
        embed.add_field(name="Discordis Bot Commands", value=botInfo)
        await client.send_message(message.channel, embed=embed)
    else:
        pass


    if message.content.upper() == '$RECRUIT':
        await client.send_message(message.channel, recruitMessage)
    else:
        pass


    if message.content.upper() == '$RULES':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/priNXCM.jpg')
        embed.add_field(name="Titles", value=titles)
        await client.send_message(message.channel, embed=embed)
    else:
        pass
    



    if message.content.upper() == '$INIT_CONTEST':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
    
    contest = ('$MUTAGEN', '$CONTEST')
    if message.content.upper() in contest:
        session = Session()
        currentUser = session.query(Member).filter_by(user=str(message.author)).first()
        if currentUser == None:
            await client.send_message(message.channel, 'You have not registered with Discord yet.  Please type $REGISTER and follow the instructions.  Thank you!')
        elif currentUser.priority == 'Mutagen Madness':
            await client.send_message(message.channel, 'You have already registered!  Thanks!')
        else:
            currentUser.priority = 'Mutagen Madness'
            session.commit()
            await client.send_message(message.channel, 'You have succesfully registered for Mutagen Madness!!  Good luck Tenno!!')
    else:
        pass



    if message.content.upper() == '$IGN':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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


    if message.content.upper() == '$MOTD':
	# Make sure we are in the right channel
        if message.channel.name == 'admin':
	    # Start database session then find clan in database
            session = Session()
            clan = session.query(Clan).filter_by(clan_name='Senua Black').first()
	    # Post to current channel this embed and the options
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Clan Name:', value=clan.clan_name)
            embed.add_field(name='Clan Research:', value=clan.clan_research)
            embed.add_field(name='Clan Events:', value=clan.clan_events)
            embed.add_field(name='Clan MOTD', value=clan.clan_priority, inline=False)
            await client.send_message(message.channel, embed=embed)
            await client.send_message(message.channel, '\n\nSelect something to change and hit [ENTER]\n\n1. Name\n2. Research\n3. Events\n4. MOTD\n\n5. View MOTD\n6. Exit')
            change = await client.wait_for_message(author=message.author)
            if str(change.content) == '1':
                await client.send_message(message.channel, 'Type the new name then hit [ENTER]')
                name = await client.wait_for_message(author=message.author)
                clan.clan_name = str(name.content)
                session.add(clan)
                session.commit()
                await client.send_message(message.channel, 'Success!')
            if str(change.content) == '2':
                await client.send_message(message.channel, 'Type in current research then hit [ENTER]')
                research = await client.wait_for_message(author=message.author)
                clan.clan_research = str(research.content)
                session.add(clan)
                session.commit()
                await client.send_message(message.channel, 'Success!')
            if str(change.content) == '3':
                await client.send_message(message.channel, 'Type in current events then hit [ENTER]')
                events = await client.wait_for_message(author=message.author)
                clan.clan_events = str(events.content)
                session.add(clan)
                session.commit()
                await client.send_message(message.channel, 'Success!')
            if str(change.content) == '4':
                await client.send_message(message.channel, 'Type MOTD then hit [ENTER]')
                motd = await client.wait_for_message(author=message.author)

                embed = discord.Embed(colour = discord.Colour.red())
                embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
                embed.add_field(name='Senua Black MOTD', value=str(motd.content))
                embed.add_field(name='Research', value='We are currently researching {0}'.format(str(clan.clan_research)), inline=False)
                await client.send_message(message.channel, embed=embed)

                await client.send_message(message.channel, '\n\nThis is what the MOTD will look like when it is displayed in #main.\n\nCommit changes?  Type Y or N then hit [ENTER]')
                commit = await client.wait_for_message(author=message.author)
                if str(commit.content).upper() == 'Y':
                    clan.clan_priority = str(motd.content)
                    session.add(clan)
                    session.commit()
                    await client.send_message(message.channel, 'Success! This will appear in #main when the first message is posted after 08:30PM CST every day.  You can also use $BLASTMOTD to send the MOTD to #main right now.  It will still be scheduled to post after 08:30PM CST as well.')
                else:
                    await client.send_message(message.channel, 'Nothing Changed!')

            if str(change.content) == '5':
                embed = discord.Embed(colour = discord.Colour.red())
                embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
                embed.add_field(name='Senua Black MOTD', value=clan.clan_priority)
                embed.add_field(name='Current Research', value='We are currently researching {0}'.format(clan.clan_research), inline=False)
                await client.send_message(message.channel, embed=embed)
                await client.send_message(message.channel, '\n\nThis will appear in #main when the first message is posted after 08:30PM CST every day.  You can also use $BLASTMOTD to send the MOTD to #main right now.  It will still be scheduled to post after 08:30PM CST as well.')

            if str(change.content) == '6':
                await client.send_message(message.channel, 'Nostalgia is the enemy of discovery')
            else:
                pass
	# If not in right channel fall to this
        else:
            await client.send_message(message.channel, 'This feature cannot be used in this channel.  If you do not know which channel to use this in then you are not supposed to be using it.')
    else:
        pass





    if message.content.upper() == '$PLANET':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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

    eidolon_variations = ['$EIDOLON', '$TERRY', '$TRIDOLON']
    if message.content.upper() in eidolon_variations:
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        await client.send_message(message.channel, 'Type TERRY then hit [ENTER] to add the Eidolon role to your profile')
        response = await client.wait_for_message(author=message.author)
        if str(response.content).upper() == 'TERRY':
            for server in client.servers:
                for role in server.roles:
                    if role.name.upper() == 'EIDOLON':
                        await client.add_roles(message.author, role)
                        await client.send_message(message.channel, 'You have successfully added the Eidolon role to your profile.  You will be notified when this role is mentioned in Discord.')
                    else:
                        continue
        else:
            await client.send_message(message.channel, 'Something went wrong.  We do not know what.  We do not know how.  But it was your own damn fault.  Start over.' )
    else:
        pass

    arby_variations = ['$ARBITRATION', '$ARBYS', '$ARBY', '$ARBITRATIONS']
    if message.content.upper() in arby_variations:
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        await client.send_message(message.channel, 'Type ARBYS then hit [ENTER] to add the Arbitration role to your profile')
        response = await client.wait_for_message(author=message.author)
        if str(response.content).upper() == 'ARBYS':
            for server in client.servers:
                for role in server.roles:
                    if role.name.upper() == 'ARBITRATIONS':
                        await client.add_roles(message.author, role)
                        await client.send_message(message.channel, 'You have successfully added the Arbitration role to your profile.  You will be notified when this role is mentioned in Discord.')
                    else:
                        continue
        else:
            await client.send_message(message.channel, 'Something went wrong.  We do not know what.  We do not know how.  But it was your own damn fault.  Start over.' )
    else:
        pass

    if message.content.upper() == '$ADDSYNDICATE':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        userStr = str(message.author)
        session = Session()
        current = session.query(Member).filter_by(user=userStr).first()
        if current == None:
            await client.send_message(message.channel, addMember)
            ign = await client.wait_for_message(author=message.author)
            # Initialize new Member Object
            current = Member(user=str(message.author), ign=str(ign.content), planet='Not Set', quest='Not Set', priority='Not Set', syndicate='Not Set')
            session.add(current)
            session.commit()
            await client.send_message(message.channel, success.format(ign.content))
        else:
            pass
        embed = discord.Embed (title = 'Warframe Status',
	    description = 'Database Information',
	    colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.set_author(name=current.ign, icon_url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name="Furthest Planet", value=current.planet)
        embed.add_field(name="Current Quest", value=current.quest)
        embed.add_field(name="Main Frame", value=current.syndicate)
        embed.add_field(name="Top Priority", value=current.priority, inline=False)
        await client.send_message(message.channel, embed=embed)
    else:
        pass


    if message.content.upper() == '$ALL':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        session = Session()
        allMembers = session.query(Member).all()
        for member in allMembers:
            if member.quest != 'DEBUG':
                await client.send_message(message.channel, "**User: {0}**   **IGN: {1}**  **Priority: {2}**".format(
                                                                                                        member.user, member.ign, member.priority))

    if message.content.upper() == "$EARTH":
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        req = Request('https://api.warframestat.us/pc/cetusCycle', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        if data['isDay'] == True:
            await client.send_message(message.channel, "It Is Currently **Day-time** On Earth With __{0}__ Left Until **Evening**.".format(data['timeLeft']))
        if data['isDay'] == False:
            await client.send_message(message.channel, "It Is Currently **Night-time** On Earth With __{0}__ Left Until **Morning**.".format(data['timeLeft']))    
    
    #  create string to search multiple words in so we can use 'when baro' or 'when the hell is baro gonna get here'
    baroMsg = str(message.content.upper())
    if ("WHEN" in baroMsg and "BARO" in baroMsg):
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        req = Request('https://api.warframestat.us/pc/voidTrader', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        if data['active'] == False:
            await client.send_message(message.channel, "Baro Ki`Teer will be arriving at **{0}** in __{1}__.".format(data['location'], data['startString']))
        else:
            pass
        if data['active'] == True:
            inventory = data['inventory']

            # Return inventory as formated text to the channel.
            await client.send_message(message.channel, "The Void Trader has already arrived!!  You can check out what he brought by typing $BARO or $TRADER.")
        else:
            pass
    else:
        pass

    if message.content.upper() == "$BARO" or message.content.upper() == '$TRADER':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        req = Request('https://api.warframestat.us/pc/voidTrader', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        if data['active'] == False:
            await client.send_message(message.channel, "Baro Ki`Teer is not here.  When will Baro be arriving you ask?")
        else:
            pass
        if data['active'] == True:
            inventory = data['inventory']

            # Return inventory as formated text to the channel.
            for stuff in inventory:
                await client.send_message(message.channel, "**{0}**  *Ducats:* __{1}__  *Credits:* __{2}__".format(stuff['item'], stuff['ducats'], stuff['credits']))
            await client.send_message(message.channel, "The Void Trader is currently at {0} and he will be leaving in {1}.\n\n".format(data['location'], data['endString']))
        else:
            pass
    else:
        pass

    if message.content.upper() == '$FORTUNA' or message.content.upper() == '$ORBVALLIS' or message.content.upper() == '$WARMCYCLE':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        req = Request('https://api.warframestat.us/pc/vallisCycle', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        if data['isWarm'] == False:
            await client.send_message(message.channel, "It is **Cold** at Orb Vallis. {0} until it is **Warm**".format(data['timeLeft']))
        else:
            pass
        if data['isWarm'] == True:
            await client.send_message(message.channel, "It is **Warm** at Orb Vallis for the next __{0}__".format(data['timeLeft']))
        else:
            pass
    else:
        pass

    if message.content.upper() == '$ENDLESS':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        req = Request('https://api.warframestat.us/pc/fissures', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        missionTypes = ('Defense', 'Survival', 'Interception', 'Excavation')
        redis_server.set('ENDLESS', 0)
        for mission in data:
            if mission['missionType'] in missionTypes:
                await client.send_message(message.channel, "**{0}**~~//~~**{1}**  *{2}*  __{3}__".format(
                                                                    mission['tier'], mission['missionType'], mission['node'], mission['eta']))
                redis_server.incr('ENDLESS')
            else:
                continue
        if int(redis_server.get('ENDLESS'))  == 0:
            await client.send_message(message.channel, "No Endless Fissure Missions available at this time.")
        else:
            pass


    if message.content.upper() == '$FISSURES':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
        req = Request('https://api.warframestat.us/pc/fissures', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        for mission in data:
            await client.send_message(message.channel, "**{0}**~~//~~**{1}**  *{2}*  __{3}__".format(
                                                                mission['tier'], mission['missionType'], mission['node'], mission['eta']))
    else:
        pass
    

    if message.content.upper() == '$DARVO':
        if message.channel.name == 'main':
            embed = discord.Embed(colour = discord.Colour.red())
            embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
            embed.add_field(name='Discordis', value='**Please use #bot for all bot commands so #main does not get cluttered.  Thanks!!**')
            await client.send_message(message.channel, embed=embed)
        else:
            pass
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
