import discord
from discord.ext import commands

TOKEN = 'NDg1MTE2NzMzMTg3OTQ4NTY0.DmsbkA.19qas06G46I6vv9aqbG9-0wm5Mg'

client = commands.Bot(command_prefix = ".")

@client.event
async def on_ready():
    print ('Discordis at your service!!  Operator?  Am I dead?')

@client.event
async def on_message(message):
    author = message.author
    content = message.content
    print( '{0} : {1}'.format(author, content))

@client.event
async def on_message_delete(message):
    author = message.author
    content = message.content
    channel = message.channel
    await client.send_message(channel, '{0}: {1}'.format(author, content))

client.run(TOKEN)