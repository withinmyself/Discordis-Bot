import asyncio
import datetime
import redis
import json
import discord
from discord.utils import get
from discord.ext import commands
from urllib.request import Request, urlopen

from senua_db import User, Session, Base, Clan, engine
from strings import welcome, bot_help, profile_help, role_help, \
                    role_guide, role_remove, current_games, full_game_names

client = commands.Bot(command_prefix = "!")
redis_server = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

@client.event
async def on_ready():
    print("Discordis Bot Ready")
    redis_server.set('ARRIVAL_COUNT', 0)  # Track users who are currently joining  
    redis_server.set('MOTD_TIMER', 0) # For displaying MOTD a certain amount of times

@client.command(pass_context=True)
async def hello(ctx, arg=None):
    channel = client.get_channel(519669330107957258)
    await channel.send('{0}'.format(arg))

@client.command(pass_context=True)
async def train(ctx, arg1=None, arg2=None):
    channel = client.get_channel(518579671613308949)
    if ctx.message.channel.name == channel.name:
        await channel.send('Whenever {0} is mentioned by anyone in any context, Discordis will reply with {1}'.format(arg1, arg2))
        if arg1 is not None:
            redis_server.set('COMMAND', str(arg1))
        if arg2 is not None:
            redis_server.set('ACTION', str(arg2))
    else:
        ctx.send('This command can only be used in the admin channel.')


@client.command(pass_context=True)
async def hour_test(ctx):
    hour_is = datetime.datetime.now().strftime('%H')
    await ctx.send(hour_is)
    hour = (int(hour_is) + 7) - 12
    if hour < 0:
        hour = 24 + int(hour)
    minute = datetime.datetime.now().strftime('%M')
    day_int = datetime.datetime.now().strftime('%w')
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day = days[int(day_int)]
    if day == -1:
        day = 'Saturday'
    time = '{0}:{1}'.format(hour, minute)
    await ctx.send('The time is {0} and the day is {1}'.format(time, day))

@client.event
async def on_member_join(member):
    server = member.guild
    role = discord.utils.get(server.roles, name='visitor')
    await member.add_roles(role)
    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
    embed.add_field(name='Thanks For Visiting!!', value=welcome)
    await member.send(embed=embed)
    founders = discord.utils.get(server.roles, name='founders')
    moderators = discord.utils.get(server.roles, name='moderators')
    hour_is = datetime.datetime.now().strftime('%H')
    hour = (int(hour_is) + 7) - 12
    if hour < 0:
        hour = 24 + int(hour)
    minute = datetime.datetime.now().strftime('%M')
    day_int = datetime.datetime.now().strftime('%w')
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day = days[int(day_int)]
    time = '{0}:{1}'.format(hour, minute)
    try:
        for founder in founders.members:
            await founder.send('We have a visitor.  {0:{1}} arrived at {2} on {3}.  Please check and see if they need any assistance.  If they want to be a part of our Gaming Server all they need to do is type !register and hit [ENTER].  They can do this in any channel.'.format(member.name, len(member.name)-4, time, day))
    except AttributeError:
        pass
    
    try:
        for member in server.members:
            for role in member.roles:
                if role.name == 'moderator':
                    await moderator.send('We have a visitor.  {0:{1}} arrived at {2} on {3}.  Please make sure they have been welcomed.  If they decide to stay all they\'ll need to do is type !register and hit [ENTER].  They can do this in any channel'.format(member.name, len(member.name)-4, time, day))
    except AttributeError:
        pass
    channel = client.get_channel(519669330107957258)
    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/7Cb9Rs9.jpg')
    embed.add_field(name='Welcome!!', value='\n\nPlease welcome {0:{1}}!  They are visiting Senua Black Gaming.  If {0:{1}} have any questions please try your best to answer.'.format(member.name, len(member.name)-4))
    await channel.send(embed=embed)


@client.event
async def on_message(message):
    command = redis_server.get('COMMAND')
    action = redis_server.get('ACTION')
    print(command, action)
    if command.upper() in message.upper():
        await message.channel.send(action)
    await client.process_commands(message)



@client.event
async def on_message(message):
    m_min = '0200'
    m_max = '1000'
    m_reset = '1010'
    m_now = datetime.datetime.now().strftime('%I%M')

    if int(m_now) >= int(m_reset):
        redis_server.set('MOTD', True)

    if redis_server.get('MOTD') == b'True' \
      and int(m_now) >= int(m_min) and int(m_now) <= int(m_max):
        redis_server.set('MOTD', False)
        channel = client.get_channel(519669330107957258)
        embed = motd_embed()
        await channel.send(embed=embed)

    await client.process_commands(message)

@client.command(pass_context=True)
async def bot(ctx, arg=None):
    if arg is None:
        await ctx.send(bot_help)
    if arg is not None:
        if arg.upper() == 'PROFILE':
            await ctx.send(profile_help)

@client.command(pass_context=True)
async def members(ctx, arg=None):
    server = ctx.message.guild
    members = []
    for member in server.members:
        members.append(member.name)
    await ctx.send(members)

@client.command(pass_context=True)
async def profile(ctx, arg1=None, arg2=None):
    x = 0
    author = ctx.message.author
    session = Session()
    profile = session.query(Clan).filter_by(clan_name=author.name).first()
    if not profile:
        new_profile = Clan(clan_name=author.name, clan_tier='Not Set', clan_level='Not Set')
        session.add(new_profile)
        session.commit()
        profile = session.query(Clan).filter_by(clan_name=author.name).first()
    if arg1 is not None:
        if arg1.upper() == 'IGN':
            profile.clan_tier=arg2
            session.commit()

        if arg1.upper() == 'ALL':
            x += 1
            server = ctx.message.guild
            session = Session()
            await ctx.send(':u55b6:   Members who have Registered   :u55b6:\n\n')
            for member in server.members:
                profile = session.query(Clan).filter_by(clan_name=member.name).first()
                if profile:
                    await ctx.send('| User: {0}    | IGN: {1}    | Favorite Games:  {2}\n'.format(
                                    profile.clan_name, profile.clan_tier, profile.clan_level))
        if arg1.upper() == 'GAME':
            profile.clan_level=arg2
            session.commit()

        if arg1.upper() == 'MINE':
            x += 1
            await ctx.send(':u55b6:  Gamer Profile  :u55b6:\n\
                :small_orange_diamond:  Discord Username: {0}\n\
                :small_orange_diamond:  Most Used IGN: {1}\n\
                :small_orange_diamond:  Game Preference: {2}'.format(
                  profile.clan_name, profile.clan_tier, profile.clan_level))

        if arg1.upper() == 'USER':
            x += 1
            if arg2 is not None:
                profile_discord = session.query(Clan).filter_by(clan_name=arg2).first()
                profile_ign = session.query(Clan).filter_by(clan_tier=arg2).first()
                if profile_discord:
                    user = profile_discord
                if profile_ign:
                    user = profile_ign
                if user:
                    await ctx.send(
                        'Discord Username: {0}\n\
                        Most Used IGN: {1}\n\
                        Game Preference: {2}'.format(
                          user.clan_name, user.clan_tier, user.clan_level))
    if x == 0:
        await ctx.send(profile_help)

@client.command(pass_context=True)
async def auto_roler(ctx):
    server = client.get_guild(475488070704168990)
    log = client.get_channel(598088764778217472)
    for member in server.members:
        activities = member.activities
        x = 0
        exists = False
        for game in full_game_names:
            if game in str(activities):
                game_role = discord.utils.get(server.roles, name=current_games[x])
                for role in member.roles:
                    if role == game_role:
                        exists = True

                if exists == False:
                    await member.add_roles(game_role)
                    x += 1
                    await log.send('Added {0} role to {1} profile.'.format(game_role.name, member.name))


@client.command(pass_context=True)
async def register(ctx, role=None):
    author = ctx.message.author
    server = ctx.message.guild

    memberRole = discord.utils.get(server.roles, name='members')
    removeRole = discord.utils.get(server.roles, name='visitor')
    if memberRole not in author.roles:
        await author.add_roles(memberRole)
        await author.remove_roles(removeRole)
        await ctx.send('The Member role was successfully added and the Visitor role has been removed.  Welcome!!')

@client.command(pass_context=True)
async def member_check(ctx):
    server = ctx.message.guild
    leaders = [128536529348853760, 467319191691722768, 444149704889204736, 319974376357363715, 384875043357982732, 246492818049073162]
    for member in server.members:
        for role in member.roles:
            if role.name == 'visitor':
                for ids in leaders:
                    leads = discord.utils.get(server.members, id=ids)
                    await leads.send('{0} still has the visitor role.  Can someone see if they need help?  If they don\'nt reply then go ahead and kick them from the server.'.format(member.name))

@client.command(pass_context=True)
async def bot_comment(ctx):
    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/t46ZqH2.png')
    embed.add_field(name='Senua Black\'s Gaming Roles', value=role_help)
    await ctx.send(embed=embed)

    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/dWBNaSY.png')
    embed.add_field(name='How It Works', value=role_guide)
    embed.add_field(name='Removing Roles', value=role_remove)
    await ctx.send(embed=embed)

@client.command(pass_context=True)
async def game_roles(ctx):
    await ctx.send('**__List of Current Game Roles__**\n\n')
    for game in current_games:
        await ctx.send('*{0}*'.format(game))

@client.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id ==598263802588430346:
        channel = client.get_channel(payload.channel_id)
        server = client.get_guild(payload.guild_id)
        member = discord.utils.get(server.members, id=payload.user_id)
        msg = await channel.fetch_message(payload.message_id)
        for game in current_games:
            if game in msg.content:
                game_role = discord.utils.get(server.roles, name=game)
                x = 0
                for role in member.roles:
                    if role == game_role:
                        x += 1
                if x == 1:
                    await member.remove_roles(game_role)
                    await member.send('The {0} role has been removed from your profile.  You will no longer be notified if anyone uses @{1}.'.format(game, game))
                else:
                    await member.send('{0} is not currently a game role that you have on your profile so nothing has been changed except the total count of members playing {1} which has been decreased by one.'.format(game, game))

@client.event
async def on_raw_reaction_add(payload):
    if payload.channel_id ==598263802588430346:
        channel = client.get_channel(payload.channel_id)
        server = client.get_guild(payload.guild_id)
        member = discord.utils.get(server.members, id=payload.user_id)
        msg = await channel.fetch_message(payload.message_id)
        for game in current_games:
            if game in msg.content:
                game_role = discord.utils.get(server.roles, name=game)
                x = 0
                for role in member.roles:
                    if role == game_role:
                        x += 1
                if x == 0:
                    await member.add_roles(game_role)
                    await member.send('{0} has been added as a role on your profile.  You will be notified if anyone uses @{1}.'.format(game, game))
                else:
                    await member.send('You already had {0} as a game role so nothing has been changed except the total count of members playing {1} which has been increased by one.'.format(game, game))


@client.command(pass_context=True)
async def blastmotd(ctx):
	channel = client.get_channel(519669330107957258)
	embed = motd_embed()
	await channel.send(embed=embed)

@client.command(pass_context=True)
async def motd(ctx, arg=None):
    embed = motd_embed()
    x = 0
    if arg:
        if arg.upper() != 'SKIP':
            for guild in client.guilds:
                for channel in guild.channels:
                    if channel.name.upper() == arg.upper():
                        await channel.send(embed=embed)
                        x += 1
                if x == 0:
                    await ctx.send('Discordis is not aware of that particular channel.  Sending MotD to this channel instead.')
                    await ctx.send(embed=embed)
    else:
        await ctx.send(embed=embed)

    if ctx.message.channel.name == 'admin':
        await ctx.send('Admin channel confirmed.  Please enter the new MotD. If you\'re happy with the current MotD and don\'t want to make any changes then type the word SKIP then hit [ENTER].')
        new_motd = await client.wait_for('message')
        if new_motd.content.upper() == 'SKIP':
            await ctx.send('Keeping MotD exactly the same.  No changes have been made whatsoever.')
        elif len(new_motd.content) >= int('1000'):
            await ctx.send('MotD has exceeded the maximum allowed size of 1,000 characters.  The old MotD has been restored for the moment.  Please start this process over and use less than 1,000 characters when updating the MotD.')
        else:
            session = Session()
            clan = session.query(Clan).filter_by(clan_name='Senua Black').first()
            clan.clan_priority = new_motd.content
            session.add(clan)
            session.commit()
            embed = motd_embed()
            await ctx.send(embed=embed)
            await ctx.send('This is exactly what the MotD will look like when it auto-posts at 8p.  Changes have already been saved.  If you need to make additional changes you will have to start from the beginning by typing !motd')

@client.command(pass_context=True)
async def warframe(ctx, arg=None):
    embed = no_bots(ctx.channel.name)
    if embed is not None:
        await ctx.message.author.send(embed=embed)
        ctx_or = ctx.message.author
    else:
        ctx_or = ctx

    if arg is None:
        await ctx_or.send('Using !warframe is easy!  Just type !warframe with any of the following commands: baro, earth, warmcycle, endless, fissures, darvo.\n\nFor example if we type: !warframe baro We get massive dissapointment!  That means it\'s working!!  Are you having fun???  I sure is.  And if you want.. you can take all the way to the bank.  The money bank.  Cause you can always count on a Cowboy. That\'s what they told me at least....\n\nDo you know who .. they are???')
    if arg is not None:
        if arg.upper() == 'EARTH':
            req = Request('https://api.warframestat.us/pc/cetusCycle', headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            data = json.loads(webpage)
            if data['isDay'] == True:
                await ctx_or.send('It Is Currently **Day-time** On Earth With __{0}__ Left Until **Evening**.'.format(data['timeLeft']))
            if data['isDay'] == False:
                await ctx_or.send('It Is Currently **Night-time** On Earth With __{0}__ Left Until **Morning**.'.format(data['timeLeft']))     

        if arg.upper() == 'BARO':
            req = Request('https://api.warframestat.us/pc/voidTrader', headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            data = json.loads(webpage)
            if data['active'] == False:
                await ctx_or.send('Baro Ki`Teer will be arriving at **{0}** in __{1}__.'.format(
                  data['location'], data['startString']))
            if data['active'] == True:
                baro_inventory = data['inventory']
                for disapointment in baro_inventory:
                    await ctx_or.send('**{0}**  *Ducats:* __{1}__  *Credits:* __{2}__'.format(
                      disapointment['item'], disapointment['ducats'], disapointment['credits']))
                await ctx_or.send('The Void Trader is currently at {0} and he will be leaving in {1}.\n\n'.format(
                  data['location'], data['endString']))

        if arg.upper() == 'WARMCYCLE':
            req = Request('https://api.warframestat.us/pc/vallisCycle', headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            data = json.loads(webpage)
            if data['isWarm'] == False:
                await ctx_or.send('It is **Cold** at Orb Vallis. {0} until it is **Warm**'.format(data['timeLeft']))
            if data['isWarm'] == True:
                await ctx_or.send('It is **Warm** at Orb Vallis for the next __{0}__'.format(data['timeLeft']))

        if arg.upper() == 'ENDLESS':
            req = Request('https://api.warframestat.us/pc/fissures', headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            data = json.loads(webpage)
            missionTypes = ('Defense', 'Survival', 'Interception', 'Excavation')
            redis_server.set('ENDLESS', 0)
            for mission in data:
                if mission['missionType'] in missionTypes:
                    await ctx_or.send( '**{0}**~~//~~**{1}**  *{2}*  __{3}__'.format(
                      mission['tier'], mission['missionType'], mission['node'], mission['eta']))
                    redis_server.incr('ENDLESS')
            if int(redis_server.get('ENDLESS'))  == 0:
                await ctx_or.send('No Endless Fissure Missions available at this time.')

        if arg.upper() == 'FISSURES':
            req = Request('https://api.warframestat.us/pc/fissures', headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            data = json.loads(webpage)
            for mission in data:
                await ctx_or.send('**{0}**~~//~~**{1}**  *{2}*  __{3}__'.format(
                  mission['tier'], mission['missionType'], mission['node'], mission['eta']))

        if arg.upper() == 'DARVO':
            req = Request('https://api.warframestat.us/pc/dailyDeals', headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            dataPack = json.loads(webpage)
            for data in dataPack:
                totalLeft = int(data['total'] - data['sold'])
                if totalLeft == 0:
                    await ctx_or.send('Darvo has sold out.  {0} is no longer available at a lower price.'.format(data['item']))
                else:
                    await ctx_or.send('**{0}**   *Original Price:* **{1}**   *Sale Price:* **{2}**   **{3} ** *Remaining*   __{4}__'.format(
                      data['item'], data['originalPrice'], data['salePrice'], totalLeft, data['eta']))


@client.command(pass_context=True)
async def kill(ctx, arg=None):
# Must be in #admin in order to use
    secure = ['roles', 'admin']
    if ctx.message.channel.name in secure:
        await client.logout()

@client.command(pass_context=True)
async def wipe(ctx, lines=1):
# 7 lines max and default is 1
    if lines <= 7:
        await ctx.channel.purge(limit=lines)

# Utility functions
def build_embed(name, value):
    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
    embed.add_field(name=name, value=value)
    return embed

def motd_embed():
	session = Session()
	clan = session.query(Clan).filter_by(clan_name='Senua Black').first()

	embed = discord.Embed(colour = discord.Colour.red())
	embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
	embed.add_field(name='Senua Black MOTD', value=clan.clan_priority)
	embed.add_field(name='Current Research', value='We are currently researching {0}'.format(clan.clan_research), inline=False)
	return embed

def no_bots(channelName):
    channel = client.get_channel(537995398187581440)
    if channelName != channel.name:
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name='Discordis', value='**Please use #bot for bot commands so our other channels do not get cluttered. Thanks!!**')
        return embed
    else:
        return None

client.run(redis_server.get('SENUA_TOKEN').decode('utf-8'))
