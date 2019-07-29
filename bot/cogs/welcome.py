import datetime

import discord
from discord.ext import commands

from admin.admin import redis_server
from admin.senua_db import User, Session, Base, Clan, engine
from admin.strings import welcome, bot_help, profile_help, role_help, \
                          role_remove, current_games, full_game_names


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

