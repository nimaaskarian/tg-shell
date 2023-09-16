#!/bin/python3

import subprocess, random, json,os
from telethon import events
from telethon.sync import TelegramClient

import utils

proxy = None
response = os.system("ping -c 1 telegram.org")
if response != 0:
    proxy =("socks5", '127.0.0.1', 40000)

creds_file = open("credentials.json")
creds = json.load(creds_file)

def main():
    with TelegramClient( creds["name"], creds["api_id"], creds["api_hash"], proxy=proxy) as client: 
        print("> BOT IS UP")

        @client.on(events.NewMessage(from_users="me"))
        async def handler(event):
            splited_message = event.message.text.split()
            try:
                command = functions_dict.get(splited_message[0])
            except Exception:
                return

            if callable(command):
                output = await command(event=event,client=client,args=splited_message[1:])
                if output is None:
                    chat = await client.get_entity(event.chat_id)
                    return await client.delete_messages(chat, [event.message.id])

                await event.message.edit(text=output)
            else:
                await event.message.edit(text=command)

        client.run_until_disconnected()

async def kick(client, event, args):
    sender = await utils.get_replied_message(client, event).sender
    chat = await client.get_entity(event.chat_id)
    permissions = await client.get_permissions(chat, 'me')
    me = await client.get_me()

    print(args)
    if permissions.is_admin and me.id != sender.id:
        await client.kick_participant(entity=chat, user=sender)
        return f"Kicked ({utils.tag_user(sender)})"

async def random_int(client, event, args):
    return str(random.randint(int(args[0]),int(args[1])))

async def shell(client, event, args):
    return subprocess.run(" ".join(args), shell=True, capture_output=True, text=True).stdout

async def whogay(client, event, args):
    chat = await client.get_entity(event.chat_id)
    users_in_chat=await client.get_participants(chat)
    if users_in_chat.total == 1:
        users_in_chat.append(await client.get_me())
    user = random.choice(users_in_chat)
    return f"{utils.tag_user(user)} is gay af"

async def send_media(client, event, args):
    print(args)
    chat = await client.get_entity(event.chat_id)
    for path in args:
        try: 
            await client.send_file(chat, path)
        except:
            await client.send_file(chat, path, force_document=True)

async def send_file(client, event, args):
    print(args)
    chat = await client.get_entity(event.chat_id)
    for path in args:
        await client.send_file(chat, path, force_document=True)

    return None

async def shell_to_file(client, event, args):
    print(args)
    return await send_file(client, event, (await shell(client, event,args)).splitlines())

async def shell_to_media(client, event, args):
    print(args)
    return await send_media(client, event, (await shell(client, event,args)).splitlines())

async def yt_dlp(client, event, args):
    message = await utils.get_replied_message(client, event)
    print(message)

async def instagram_add_dd(client, event, args):
    message = await utils.get_replied_message(client, event)
    return message.message.replace("instagram", "ddinstagram")

async def tag_everyone(client, event, args):
    chat = await client.get_entity(event.chat_id)
    return " ".join([utils.tag_user(user) for user in await client.get_participants(chat)])
    
functions_dict = {
'kick': kick,
'rand':  random_int,
'shell':  shell, 
'rtfw': "https://wiki.archlinux.org",
'whogay': whogay,
'file': send_file,
'medi': send_media,
'shfile': shell_to_file,
'shmedi': shell_to_media,
'dl': yt_dlp,
'dd': instagram_add_dd,
'everyone': tag_everyone,
}

if __name__ == "__main__":
    main()