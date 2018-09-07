



def cetus_time (message):
    if message.content.upper() == "CETUS":
        req = Request('https://api.warframestat.us/pc/cetusCycle', headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        if data['isDay'] == True:
            for server in client.servers:
                for channel in server.channels:
                    if channel.name == 'what':
                        await client.send_message(channel, "It Is Currently Day Time At Cetus With {} Left Until Night".format(data['timeLeft']))
        if data['isDay'] == False:
            for server in client.servers:
                for channel in server.channels:
                    if channel.name == 'what':
                        await client.send_message(channel, "It Is Currently Night Time At Cetus With {} Left Until Morning".format(data['timeLeft']))

# def planet_me (message):
#    if message.content.upper() == '$PLANET':
#        await client.send_message(message.channel, "What Planet Are You On? Use $Planet")
#        if message.content.upper() == '$EARTH':
#             add_roles(message.member, *New Loka)