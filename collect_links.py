import configparser
import json
import re
from telethon.tl.functions.channels import GetFullChannelRequest



from telethon.sync import TelegramClient

# if need proxy unmark
# from telethon import connection

# classes for work with channels
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# class for work with messages
from telethon.tl.functions.messages import GetHistoryRequest

# Getting accounting info
# section [Telegram]
# api_id = ...
# api_hash = ...
# username = ...
config = configparser.ConfigParser()
config.read("cfg.ini")

api_id   = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

# if need proxy unmark
# proxy = (proxy_server, proxy_port, proxy_key)

client = TelegramClient(username, api_id, api_hash) #,
# if need proxy unmark
#    connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
#    proxy=proxy)

client.start()


async def collect_urls(channel):
    offset_msg = 0
    limit_msg = 100

    all_messages = []
    total_messages = 0
    total_count_limit = 0

    links = set()

    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
#            all_messages.append(message.to_dict())
            if type(message.message) is str:
#                print(message.message)
                for l in re.findall(r'(https://t.me/[\S]+/)', message.message):
                    links.add(l)
#                    print(l)
#                print(type(re.findall(r'(https://t.me/[\S]+/)', message.message)))
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
    return(links)


async def main():
    url = 'https://t.me/IronDrovosek/'
    channel = await client.get_entity(url)
    ch_full = await client(GetFullChannelRequest(channel))
    print(ch_full.full_chat)
    lnks = await collect_urls(channel)
    for url in lnks:
        try:
            print("\n-----\nTelegam channel", url)
            channel = await client.get_entity(url)
            ch_full = await client(GetFullChannelRequest(channel))
            print(ch_full.full_chat.about, "\n")
        except:
            print("Can't connect to channel", url)

with client:
    client.loop.run_until_complete(main())


