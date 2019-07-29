import datetime

import discord
from discord.ext import commands

from admin.admin import redis_server, client
from admin.senua_db import User, Session, Base, Clan, engine
from admin.strings import welcome, bot_help, profile_help, role_help, \
                          role_remove, current_games, full_game_names

class General(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(pass_context=True)
    async def plagueis(self, ctx):
        await ctx.send(darth)

    @commands.command(pass_context=True)
    async def profile(self, ctx, arg1=None, arg2=None):
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

    @commands.command(pass_context=True)
    async def register(self, ctx, role=None):
        author = ctx.message.author
        server = ctx.message.guild

        memberRole = discord.utils.get(server.roles, name='members')
        removeRole = discord.utils.get(server.roles, name='visitor')
        if memberRole not in author.roles:
            await author.add_roles(memberRole)
            await author.remove_roles(removeRole)
            await ctx.send('The Member role was successfully added and the Visitor role has been removed.  Welcome!!')

