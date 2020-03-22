import redis

from discord.ext import commands

redis_server = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
client = commands.Bot(command_prefix = "!")

