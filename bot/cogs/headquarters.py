import datetime
import discord
from discord.ext import commands
from admin.admin import redis_server, client
from admin.senua_db import User, Session, Base, Clan, engine
from admin.strings import role_ids, full_game_names, current_games, role_remove, \
                          role_guide, role_help, profile_help, bot_help, darth, welcome

class Headquarters(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(pass_context=True, hidden=True)
    async def kill(self, ctx):
        if ctx.message.channel.name == 'admin':
            await client.logout()


    @commands.command(pass_context=True, hidden=True)
    async def members(self, ctx, arg=None):
        server = ctx.message.guild
        members = []
        for member in server.members:
            members.append(member.name)
        await ctx.send(members)

    @commands.command(pass_context=True, hidden=True)
    async def auto_roler(self, ctx):
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

    @commands.command(pass_context=True, hidden=True)
    async def member_check(self, ctx):
        server = ctx.message.guild
        leaders = [128536529348853760, 467319191691722768, 444149704889204736, 319974376357363715, 384875043357982732, 246492818049073162]
        for member in server.members:
            for role in member.roles:
                if role.name == 'visitor':
                    for ids in leaders:
                        leads = discord.utils.get(server.members, id=ids)
                        await leads.send('{0} still has the visitor role.  Can someone see if they need help?  If they don\'nt reply then go ahead and kick them from the server.'.format(member.name))
    @commands.command(pass_context=True, hidden=True)
    async def game_roles(self, ctx):
        await ctx.send('**__List of Current Game Roles__**\n\n')
        for game in current_games:
            await ctx.send('*{0}*'.format(game))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
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

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
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

    @commands.command(pass_context=True, hidden=True)
    async def check(self, ctx, arg=None):
        channel = ctx.message.channel
        if channel.name == 'leaders' or channel.name == 'leaders_check' or channel.name == 'admin':
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
            await ctx.send('This command is only usable in the following channels: leaders, leaders_check, admin.')

    @commands.command(pass_context=True)
    async def leaders(self, ctx):
        checked_in = []
        server = ctx.message.guild
        for role in server.roles:
            if role.name == 'founders' or role.name == 'moderators':
                for member in role.members:
                    if redis_server.get(member.name) == b'True':
                        checked_in.append(member.name)
        await ctx.send('The following leaders should be available for Warframe invites or any other questions you may have: {0}'.format(checked_in))


    @commands.command(pass_context=True, hidden=True)
    async def blastmotd(self, ctx):
        channel = client.get_channel(519669330107957258)
        embed = _motd_embed()
        await channel.send(embed=embed)

    @commands.command(pass_context=True, hidden=True)
    async def motd(self, ctx, arg=None):
        embed = _motd_embed()
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
                embed = _motd_embed()
                await ctx.send(embed=embed)
                await ctx.send('This is exactly what the MotD will look like when it auto-posts at 8p.  Changes have already been saved.  If you need to make additional changes you will have to start from the beginning by typing !motd')

    def _build_embed(self, name, value):
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name=name, value=value)
        return embed

    def _motd_embed(self):
        session = Session()
        clan = session.query(Clan).filter_by(clan_name='Senua Black').first()
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name='Senua Black MOTD', value=clan.clan_priority)
        embed.add_field(name='Current Research', value='We are currently researching Anti Violet.  The Pigments required are obtained from the Zanuka Hunter.  We need 10 total pigments.  Each Zanuka encounter only provides 1.  So we are going to need a lot of help getting all 10.  Let us know if you have any questions about how you can help.', inline=False)
        return embed
