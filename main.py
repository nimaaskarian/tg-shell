#!/bin/python3

import subprocess, random, json, re, math
from http.client import HTTPConnection

from telethon import events
from telethon.sync import TelegramClient

import utils

proxy = None
try:
    connection = HTTPConnection("telegram.org", port=80, timeout=1)
    connection.request("HEAD", "/")
except:
    proxy =("socks5", '127.0.0.1', 40000)

creds_file = open("credentials.json")
creds = json.load(creds_file)

def main():
    with TelegramClient( creds["name"], creds["api_id"], creds["api_hash"], proxy=proxy) as client: 
        print("> BOT IS UP")

        @client.on(events.NewMessage(from_users="me"))
        async def handler(event):
            splited_message = event.message.text.split()
            inside_message_pattern = r"```.+?```"
            matches = re.findall(inside_message_pattern, event.message.text)
            if len(matches):
                splited_message = matches[0].replace("```","").split()
            try:
                command = functions_dict[splited_message[0]]
            except Exception:
                return

            if callable(command):
                output = await command(event=event,client=client,args=splited_message[1:])
                if output is None:
                    chat = await client.get_entity(event.chat_id)
                    return await client.delete_messages(chat, [event.message.id])
                if len(matches):
                    event.message.text = event.message.text.replace(matches[0], output)
                else:
                    event.message.text = output

                if len(matches) > 1:
                    return await handler(event)
                else:
                    await event.message.edit(text=event.message.text)
            else:
                await event.message.edit(text=command)

        client.run_until_disconnected()

async def kick(client, event, args):
    should_get_kicked = []
    for arg in args:
        id_pattern = re.compile(r"\[.*\]\(tg://user\?id=\d+\)")

        id_match = id_pattern.match(arg)
        if id_match:
            should_get_kicked.append(await client.get_entity(int(id_match.group(1))))
            continue

        username_pattern = re.compile("^@.*")
        username_match = username_pattern.match(arg)

        if username_match:
            should_get_kicked.append(await client.get_entity(username_match.group(0)))
            continue

    reply_sender = (await utils.get_replied_message(client, event)).sender
    should_get_kicked.append(reply_sender)

    chat = await client.get_entity(event.chat_id)
    permissions = await client.get_permissions(chat, 'me')

    tags =  []
    for user in should_get_kicked:
        if permissions.is_admin and not user.is_self:
            await client.kick_participant(entity=chat, user=user)
            tags.append(utils.tag_user(user))
    return f"Kicked {', '.join(tags)}"

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
    chat = await client.get_entity(event.chat_id)
    for path in args:
        try: 
            await client.send_file(chat, path)
        except:
            await client.send_file(chat, path, force_document=True)

async def send_file(client, event, args):
    chat = await client.get_entity(event.chat_id)
    for path in args:
        await client.send_file(chat, path, force_document=True)

    return None

async def shell_to_file(client, event, args):
    return await send_file(client, event, (await shell(client, event,args)).splitlines())

async def shell_to_media(client, event, args):
    return await send_media(client, event, (await shell(client, event,args)).splitlines())

async def yt_dlp(client, event, args):
    message = await utils.get_replied_message(client, event)

async def instagram_add_dd(client, event, args):
    message = await utils.get_replied_message(client, event)
    chat = await client.get_entity(event.chat_id)
    await client.send_message(chat,message.message.replace("instagram", "ddinstagram"), reply_to=message)

async def tag_everyone(client, event, args):
    chat = await client.get_entity(event.chat_id)
    message = await utils.get_replied_message(client, event)
    tags = " ".join([utils.tag_user(user) for user in await client.get_participants(chat) if not user.bot and not user.is_self])
    try:
        await client.send_message(chat,tags, reply_to=message)
    except:
        await client.send_message(chat,tags)

async def eval_python(client, event, args):
    return str(eval(" ".join(args)))
    
async def exec_python(client, event, args):
    return str(exec(" ".join(args)))

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
'eval': eval_python,
'exec': exec_python,
}

if __name__ == "__main__":
    main()
