import json
from urllib.request import Request, urlopen

import discord
from discord.ext import commands

from admin.admin import redis_server, client
from admin.senua_db import User, Session, Base, Clan, engine
from admin.strings import role_ids, full_game_names, current_games, role_remove, \
                          role_guide, role_help, profile_help, bot_help, darth, welcome


class Tenno(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(pass_context=True)
    async def warframe(self, ctx, arg=None):

        if arg is None or arg.upper() == 'HELP':
            await ctx.send('Using !warframe is easy!  Just type !warframe followed with any of the following commands: baro, earth, warmcycle, endless, fissures, darvo')
        if arg is not None:
            if arg.upper() == 'EARTH':
                req = Request('https://api.warframestat.us/pc/cetusCycle', headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                data = json.loads(webpage)
                if data['isDay'] == True:
                    await ctx.send('It Is Currently **Day-time** On Earth With __{0}__ Left Until **Evening**.'.format(data['timeLeft']))
                if data['isDay'] == False:
                    await ctx.send('It Is Currently **Night-time** On Earth With __{0}__ Left Until **Morning**.'.format(data['timeLeft']))     

            if arg.upper() == 'BARO':
                req = Request('https://api.warframestat.us/pc/voidTrader', headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                data = json.loads(webpage)
                if data['active'] == False:
                    await ctx.send('Baro Ki`Teer will be arriving at **{0}** in __{1}__.'.format(
                      data['location'], data['startString']))
                if data['active'] == True:
                    baro_inventory = data['inventory']
                    for disapointment in baro_inventory:
                        await ctx.send('**{0}**  *Ducats:* __{1}__  *Credits:* __{2}__'.format(
                          disapointment['item'], disapointment['ducats'], disapointment['credits']))
                    await ctx.send('The Void Trader is currently at {0} and he will be leaving in {1}.\n\n'.format(
                      data['location'], data['endString']))

            if arg.upper() == 'WARMCYCLE':
                req = Request('https://api.warframestat.us/pc/vallisCycle', headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                data = json.loads(webpage)
                if data['isWarm'] == False:
                    await ctx.send('It is **Cold** at Orb Vallis. {0} until it is **Warm**'.format(data['timeLeft']))
                if data['isWarm'] == True:
                    await ctx.send('It is **Warm** at Orb Vallis for the next __{0}__'.format(data['timeLeft']))

            if arg.upper() == 'ENDLESS':
                req = Request('https://api.warframestat.us/pc/fissures', headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                data = json.loads(webpage)
                missionTypes = ('Defense', 'Survival', 'Interception', 'Excavation')
                redis_server.set('ENDLESS', 0)
                for mission in data:
                    if mission['missionType'] in missionTypes:
                        await ctx.send( '**{0}**~~//~~**{1}**  *{2}*  __{3}__'.format(
                          mission['tier'], mission['missionType'], mission['node'], mission['eta']))
                        redis_server.incr('ENDLESS')
                if int(redis_server.get('ENDLESS'))  == 0:
                    await ctx.send('No Endless Fissure Missions available at this time.')

            if arg.upper() == 'FISSURES':
                req = Request('https://api.warframestat.us/pc/fissures', headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                data = json.loads(webpage)
                for mission in data:
                    await ctx.send('**{0}**~~//~~**{1}**  *{2}*  __{3}__'.format(
                      mission['tier'], mission['missionType'], mission['node'], mission['eta']))

            if arg.upper() == 'DARVO':
                req = Request('https://api.warframestat.us/pc/dailyDeals', headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                dataPack = json.loads(webpage)
                for data in dataPack:
                    totalLeft = int(data['total'] - data['sold'])
                    if totalLeft == 0:
                        await ctx.send('Darvo has sold out.  {0} is no longer available at a lower price.'.format(data['item']))
                    else:
                        await ctx.send('**{0}**   *Original Price:* **{1}**   *Sale Price:* **{2}**   **{3} ** *Remaining*   __{4}__'.format(
                          data['item'], data['originalPrice'], data['salePrice'], totalLeft, data['eta']))

