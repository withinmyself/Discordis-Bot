


def channel_finder(channel, client):
    for server in client.servers:
        for channel in server.channels:
            if channel.name == str(channel):
                return channel
            else:
                continue
    return None