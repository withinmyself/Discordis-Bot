from cogs.headquarters import Headquarters
from cogs.welcome import Welcome
from cogs.warframe import Tenno
from cogs.general import General
from admin.admin import redis_server, client

client.add_cog(Headquarters(client))
client.add_cog(Welcome(client))
client.add_cog(Tenno(client))
client.add_cog(General(client))

client.run(redis_server.get('SENUA_TOKEN').decode('utf-8'))

