from discord.ext import commands
from discord.utils import get
from admin.admin import redis_server


class Test(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(pass_context=True)
    async def you_test(self, ctx):
        server = ctx.message.guild
        role = get(server.roles, name='visitor')
        redis_server.set('TEST', True)
        await ctx.send('TEST {0}{1}'.format(role, redis_server.get('TEST')))
