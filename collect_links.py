import configparser
import json
import re
from telethon.tl.functions.channels import GetFullChannelRequest
import networkx as nx
import matplotlib
import os


from telethon.sync import TelegramClient


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
proxy_server = config['Telegram']['proxy_server']
proxy_port = int(config['Telegram']['proxy_port'])
proxy_key = config['Telegram']['proxy_key']
start_channel = config['Telegram']['start_channel']
tg_timeout = int(config['Telegram']['timeout'])

interest = re.split(r'#',(config['Save']['interest']))
fpath = config['Save']['folder']
        
if not os.path.isdir(fpath):
    print('Can I create folder: ', fpath,'?')
    if input() == 'y':
        try:
            os.mkdir(fpath)
        except:
            print ('I can\'t create folder ', fpath)
            sys.exit()
        else:
            print ('Created folder ', fpath)
    else:
        sys.exit()
         

# if need proxy 
proxy = (proxy_server, proxy_port, proxy_key)

try:
    client = TelegramClient(username, api_id, api_hash, timeout=tg_timeout)
    client.start()
except ConnectionError:
    print('attempt with proxy')
    from telethon import connection
    client = TelegramClient(username, api_id, api_hash,
       connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
       proxy=proxy, timeout=tg_timeout)
    client.start()
#except Exception as ex:
#    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
#    message = template.format(type(ex).__name__, ex.args)
#    print(message)


G = nx.DiGraph()


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
            # all_messages.append(message.to_dict())
            if type(message.message) is str:
                for r in interest:
                    if re.search(r.lower(), message.message.lower()):
                        print('r = ',r, ', message = ', message.message)
                for l in re.findall(r'(https://t.me/[\S]+/)', message.message):
                    links.add(l)
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
    return(links)


async def add_tg_channels(url):

    try:
        channel = await client.get_entity(url)
        ch_full = await client(GetFullChannelRequest(channel))
        print("\n-----\nTelegam channel", url)
        print(ch_full.full_chat.about)

        file_name = url[12:len(url)-1]
        print('Filename ', fpath+file_name)
        try:
            file_channel = open(fpath+file_name, 'w')
            json.dump(ch_full.full_chat.to_json(), file_channel)
            print('ch_full\n',dir(ch_full))
            print('ch_full.full_chat\n',dir(ch_full.full_chat))
#            file_channel.write(dir(ch_full.full_chat.about))
#'about', 'admins_count', 'available_min_id', 'banned_count', 'bot_info', 'can_set_location', 'can_set_stickers', 'can_set_username', 'can_view_participants', 'can_view_stats', 'chat_photo', 'exported_invite', 'folder_id', 'from_reader', 'has_scheduled', 'hidden_prehistory', 'id', 'kicked_count', 'linked_chat_id', 'location', 'migrated_from_chat_id', 'migrated_from_max_id', 'notify_settings', 'online_count', 'participants_count', 'pinned_msg_id', 'pretty_format', 'pts', 'read_inbox_max_id', 'read_outbox_max_id', 'serialize_bytes', 'serialize_datetime', 'slowmode_next_send_date', 'slowmode_seconds', 'stickerset', 'stringify', 'to_dict', 'to_json', 'unread_count']
            file_channel.close()
        except Exception as ex:
            print('can\'t write to file')
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

        lnks = await collect_urls(channel)
        print('lnks',lnks)
        # urls.update(lnks)
        # print("urls",urls)
        for u in lnks:
            print(u)
            if u in G.nodes:
                print(u," in ")
                G.add_edge(url,u)
                continue
            G.add_edge(url,u)
            nx.write_gml(G, "./test")
            await add_tg_channels(u)
    except Exception as ex:
        print("Can't connect to channel", url)
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)


async def main():
    G.add_node(start_channel)
    nx.write_gml(G, "./test")
    await add_tg_channels(start_channel)

with client:
    client.loop.run_until_complete(main())


