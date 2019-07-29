import asyncio
import datetime
#import redis
import json
import discord
from discord.utils import get
from discord.ext import commands
from urllib.request import Request, urlopen

from cogs.test import Test
from admin.admin import redis_server, client
from admin.senua_db import User, Session, Base, Clan, engine
from strings import welcome, bot_help, profile_help, role_help, \
                    role_guide, role_remove, current_games, full_game_names, darth

#client = commands.Bot(command_prefix = "!")
#redis_server = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)


class Welcome(commands.Cog):
   def __init__ (self, bot):
       self.bot = bot
       self._last_member = None

   @commands.Cog.listener()
   async def on_ready(self):
       print("Discordis Bot Ready")

   @commands.Cog.listener()
   async def on_member_join(self, member):
       server = member.guild
       role = discord.utils.get(server.roles, name='visitor')
       await member.add_roles(role)

       checked_in = []
       server = member.guild
       for role in server.roles:
           if role.name == 'founders' or role.name == 'moderators':
               for leader in role.members:
                   if redis_server.get(leader.name) == b'True':
                       checked_in.append(leader.name)
       if len(checked_in) == 0:
           redis_server.set('CHECK', False)
           embed = discord.Embed(colour = discord.Colour.red())
           embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
           embed.add_field(name='Thanks For Visiting!!', value='Welcome to Senua Black!!  None of our leaders are currently available for immediate assistance.  You can send a private message to withinmyself, PJtheBatman, gahro_nahvah or Sadism to hopefully grab our attention.  For now feel free to say hello in our main chat channel.  We try not to make any of our members wait too long in these situations.  Once we are able to get a Clan invite sent you will be able to change your status from visitor to member in Discord which will give you full access to the rest of our channels.')
           await member.send(embed=embed)
       else:
           redis_server.set('CHECK', True)
           list_to_string = ''
           for word in checked_in:
               if word == checked_in[len(checked_in)-1] and len(checked_in) > 1:
                   list_to_string = list_to_string + ' or ' + word
               elif len(checked_in) == 1:
                   list_to_string = word
               else:
                   list_to_string = list_to_string + word + ', '

           redis_server.set('CHECKEDIN', list_to_string)
           embed = discord.Embed(colour = discord.Colour.red())
           embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
           embed.add_field(name='Thanks For Visiting!!', value='Welcome to Senua Black!!  For immediate assistance regarding Warframe invites or any other questions you can private message {0}.  Feel free to also say hello in our main chat channel.  Once you have been made a member in Warframe you can change your status from visitor to member in Discord which will give you full access to the rest of our channels.'.format(list_to_string))
           await member.send(embed=embed)

       founders = discord.utils.get(server.roles, name='founders')
       moderators = discord.utils.get(server.roles, name='moderators')
       daytime = self._time_format()
       check = ''
       if redis_server.get('CHECK') == b'False':
           check = 'There is currently no-one checked in for immediate assistance.'
       else:
           check = 'These are the current leaders checked in for immediate assistance: {0}'.format(redis_server.get('CHECKEDIN').decode('utf-8'))
       try:
           for founder in founders.members:
               await founder.send('We have a visitor.  {0:{1}} arrived at {2} on {3}.  Please check and see if they need any assistance.  If they want to be a part of our Gaming Server all they need to do is type !register and hit [ENTER].  They can do this in any channel.  {4}'.format(member.name, len(member.name)-4, daytime[1], daytime[0], check))
       except AttributeError:
           pass
       try:
           for member in server.members:
               for role in member.roles:
                   if role.name == 'moderator':
                       await moderator.send('We have a visitor.  {0:{1}} arrived at {2} on {3}.  Please make sure they have been welcomed.  If they decide to stay all they\'ll need to do is type !register and hit [ENTER].  They can do this in any channel.  {4}'.format(member.name, len(member.name)-4, daytime[1], daytime[0], check))
       except AttributeError:
           pass
       channel = client.get_channel(519669330107957258)
       embed = discord.Embed(colour = discord.Colour.red())
       embed.set_thumbnail(url='https://i.imgur.com/7Cb9Rs9.jpg')
       embed.add_field(name='Welcome!!', value='\n\nPlease welcome {0:{1}}!  They are visiting Senua Black Gaming.  If {0:{1}} have any questions please try your best to answer.'.format(member.name, len(member.name)-4))
       await channel.send(embed=embed)


   @commands.Cog.listener()
   async def on_message(self, message):
       m_min = '0200'
       m_max = '1000'
       m_reset = '1010'
       m_now = datetime.datetime.now().strftime('%H%M')

       if int(m_now) >= int(m_reset):
           redis_server.set('MOTD', True)

       if redis_server.get('MOTD') == b'True' and int(m_now) >= int(m_min) and int(m_now) <= int(m_max):
           redis_server.set('MOTD', False)
           channel = client.get_channel(594455094355820544)
           embed = motd_embed()
           await channel.send(embed=embed)
           await client.process_commands(message)

   @commands.command(pass_context=True)
   async def guide(self, ctx, arg=None):
       if arg is None:
           await ctx.send(bot_help)
       if arg is not None:
           if arg.upper() == 'HELP':
               await ctx.send(bot_help)

   def _time_format(self):
       hour_is = datetime.datetime.now().strftime('%H')
       hour = (int(hour_is) + 7) - 12
       if hour < 0:
           hour = 24 + int(hour)
       minute = datetime.datetime.now().strftime('%M')
       day_int = datetime.datetime.now().strftime('%w')
       days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
       day = days[int(day_int)]
       time = '{0}:{1}'.format(hour, minute)
       return [day, time]


   @commands.command(pass_context=True, hidden=True)
   async def hello(self, ctx, say=None, channel=None):
       if channel is None:
          channel = discord.client.get_channel(519669330107957258)
       else:
           server = ctx.message.guild
           channel = discord.utils.get(server.channels, name=str(channel))
       if say is None:
           say = 'Hello!'
       await channel.send('{0}'.format(arg))

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None


    @commands.command(pass_context=True, hidden=True)
    async def members(self, ctx, hidden=True, arg=None):
        server = ctx.message.guild
        members = []
        for member in server.members:
            members.append(member.name)
        await ctx.send(members)


@client.command(pass_context=True)
async def plagueis(ctx):
    await ctx.send(darth)


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

@client.command(pass_context=True, hidden=True)
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

@client.command(pass_context=True, hidden=True)
async def member_check(ctx):
    server = ctx.message.guild
    leaders = [128536529348853760, 467319191691722768, 444149704889204736, 319974376357363715, 384875043357982732, 246492818049073162]
    for member in server.members:
        for role in member.roles:
            if role.name == 'visitor':
                for ids in leaders:
                    leads = discord.utils.get(server.members, id=ids)
                    await leads.send('{0} still has the visitor role.  Can someone see if they need help?  If they don\'nt reply then go ahead and kick them from the server.'.format(member.name))

@client.command(pass_context=True, hidden=True)
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

@client.command(pass_context=True, hidden=True)
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

@client.command(pass_context=True, hidden=True)
async def check(ctx, arg=None):
    channel = ctx.message.channel
    if channel.name == 'leaders':
        member = ctx.message.author
        name = str(member.name)
        if redis_server.get(name) == None or redis_server.get(name) == b'True':
            redis_server.set(name, True)
            available = 'checked in'
        elif redis_server.get(name) == b'False':
            available = 'checked out'
        else:
            available = 'not set yet'
        if str(arg).upper() == 'IN':
            redis_server.set(name, True)
            available = 'checked in'
            await ctx.send('Successfully {0}'.format(available))
        elif str(arg).upper() == 'OUT':
            redis_server.set(name, False)
            available = 'checked out'
            await ctx.send('Successfully {0}'.format(available))
        else:
            await ctx.send('Instructions for !check:\n\nMake yourself available for in-game Warframe invites and Discord support:  !check in\nTurn off all notifications regarding Warframe invites, Visitor status and Discord support:  !check out\n\nYour current availability status is {0}.'.format(available))
    else:
        await ctx.send('This command is only usable in the leaders channel.')

@client.command(pass_context=True)
async def leaders(ctx):
    checked_in = []
    server = ctx.message.guild
    for role in server.roles:
        if role.name == 'founders' or role.name == 'moderators':
            for member in role.members:
                if redis_server.get(member.name) == b'True':
                    checked_in.append(member.name)
    await ctx.send('The following leaders should be available for Warframe invites or any other questions you may have: {0}'.format(checked_in))


@client.command(pass_context=True, hidden=True)
async def blastmotd(ctx):
	channel = client.get_channel(519669330107957258)
	embed = motd_embed()
	await channel.send(embed=embed)

@client.command(pass_context=True, hidden=True)
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

    if arg is None or arg.upper() == 'HELP':
        await ctx_or.send('Using !warframe is easy!  Just type !warframe followed with any of the following commands: baro, earth, warmcycle, endless, fissures, darvo')
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


@client.command(pass_context=True, hidden=True)
async def kill(ctx, arg=None):
# Must be in #admin in order to use
    secure = ['roles', 'admin']
    if ctx.message.channel.name in secure:
        await client.logout()

@client.command(pass_context=True, hidden=True)
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
	embed.add_field(name='Current Research', value='We are currently researching Anti Violet.  The Pigments required are obtained from the Zanuka Hunter.  We need 10 total pigments.  Each Zanuka encounter only provides 1.  So we are going to need a lot of help getting all 10.  Let us know if you have any questions about how you can help.', inline=False)
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
client.add_cog(Welcome(client))
client.add_cog(Admin(client))
client.add_cog(Test(client))
client.run(redis_server.get('SENUA_TOKEN').decode('utf-8'))
