import asyncio
import time
import redis
import json
import random
import schedule

import discord
from discord.utils import get
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



@client.event
async def on_ready():
    print("Discordis Bot Ready")
    redis_server.set('ARRIVAL_COUNT', 0)  # Track users who are currently joining  
    redis_server.set('MOTD_TIMER', 0) # For displaying MOTD a certain amount of times


@client.event
async def on_member_join(member):
	server = ctx.message.guild
	role = discord.utils.get(server.roles, name='Visitor')
	member.add_roles(role)

    embed = discord.Embed(colour = discord.Colour.red())
    embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
    embed.add_field(name='Thanks For Visiting!!', value=welcome)
    await member.send(embed=embed)

	channel = client.get_channel(519669330107957258)
	embed = discord.Embed(colour = discord.Colour.red())
	embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
	embed.add_field(name='Welcome!!', value='@guest\n\nPlease welcome {0:{1}}!  They are visiting Senua Black Gaming.  If {0:{1}} have any questions please try your best to answer.'.format(member.name, len(member.name)-4))
	await channel.send(embed=embed)

@client.event
async def on_message(message):
    def redis_motd():
        redis_server.set('MOTD', True)
    schedule.every().day.at("19:30").do(redis_motd)
    schedule.run_pending()
    time.sleep(1)

    if redis_server.get('MOTD') == b'True':
        redis_server.set('MOTD', False)
        channel = client.get_channel(519669330107957258)
		embed = motd_embed()
		await channel.send(embed=embed)

@client.command(pass_context=True)
async def register(ctx, role=None):
    author = ctx.message.author
    server = ctx.message.guild
    adminRoles = ['Admin', 'Warlords & Robots', 'Artist', 'Warlord', 'Moderator', 'Generals', 'Promoter', 'Founder', 'Bot']
    
    if role is not None:
        argRole = discord.utils.get(server.roles, name=str(role))
        if argRole and role not in adminRoles:
            await author.add_roles(argRole)
            await ctx.send('The {0} role was successfully added.'.format(role))
        else:
            await ctx.send('The role you provided does not exist or is not allowed to be added this way.')
    
    memberRole = discord.utils.get(server.roles, name='Member')
    await author.add_roles(memberRole)
    await ctx.send('The Member role was successfully added')

@client.command(pass_context=True)
async def blastmotd(ctx):
	channel = client.get_channel(519669330107957258)
	embed = motd_embed()
	await channel.send(embed=embed)

@client.command(pass_context=True)
 async def motd(ctx, arg=None):
    channel = ctx.channel.name
    embed = motd_embed()
    await ctx.send(embed=embed)
    if channel == 'admin':
        await ctx.send('Admin channel confirmed.  Submit the new MotD.')
        new_motd = await client.wait_for('message')
        session = Session()
        clan = session.query(Clan).filter_by(clan_name='Senua Black').first()
        clan.clan_priority = new_motd.content
        session.add(clan)
        session.commit()
        embed = motd_embed()
        await ctx.send(embed=embed)

@client.command(pass_context=True)                                                                                                                  76 
async def warframe(ctx, arg=None):
    channelName = ctx.channel.name
    embed = no_bots(channelName)
    if embed is not None:
        await ctx.send(embed=embed)
	
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

# You must be in #admin in order to use !kill and !clear
@client.command(pass_context=True)
async def kill(ctx, arg=None):
		if ctx.message.channel.name == 'admin':
            await client.logout()

@client.command(pass_context=True)
async def clear(ctx, lines=1):
		if ctx.message.channel.name == 'admin':
            await client.purge_from(ctx.message.channel, limit=lines)      

def motd_embed():
	session = Session()
	clan = session.query(Clan).filter_by(clan_name='Senua Black').first()

	embed = discord.Embed(colour = discord.Colour.red())
	embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
	embed.add_field(name='Senua Black MOTD', value=clan.clan_priority)
	embed.add_field(name='Current Research', value='We are currently researching {0}'.format(clan.clan_research), inline=False)
	return embed

def no_bots(channelName):
    channel = client.get_channel(518579671613308949)
    if channelName == channel.name:
        embed = discord.Embed(colour = discord.Colour.red())
        embed.set_thumbnail(url='https://i.imgur.com/6cyxnVY.png')
        embed.add_field(name='Discordis', value='**Please use #bot for bot commands so #main does not get cluttered.  Thanks!!**')
        return embed
    else:
        return None

client.run(redis_server.get('SENUA_TOKEN').decode('utf-8'))
