#!/bin/python3

import subprocess, random, json, re, math, io
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
        @client.on(events.NewMessage(chats="nerdemojialert"))
        async def handler(event, recursive=False):
            inside_message_pattern = r"(?<!\\)```.*?```"
            matches = re.findall(inside_message_pattern, event.message.text)
            message=event.message.text

            if len(matches):
                message = matches[0].replace("```","")
            splited_message = message.split()
            try:
                command = functions_dict[splited_message[0]]
            except Exception:
                if recursive:
                    await event.message.edit(text=event.message.text)
                return

            if callable(command):
                output = await command(
                    client=client,
                    event=event,
                    args=splited_message[1:],
                    message=message,
                    )
                if output is None:
                    chat = await client.get_entity(event.chat_id)
                    return await client.delete_messages(chat, [event.message.id])
                if len(matches):
                    event.message.text = event.message.text.replace(matches[0], output)
                    return await handler(event,True)
                else:
                    event.message.text = output

                await event.message.edit(text=event.message.text)
            else:
                if recursive:
                    await event.message.edit(text=command)
                else:
                    event.message.text = command
                    return await handler(event, True)

        client.run_until_disconnected()

async def kick(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    should_get_kicked = []
    if event.message.entities:
        for entity in event.message.entities:
            id_pattern = re.compile(r"tg://user\?id=\d+")

            try:
                id_match = id_pattern.match(entity.url)
            except:
                continue
            if id_match:
                should_get_kicked.append(await client.get_entity(int(id_match.group(0).replace("tg://user?id=", ""))))

    for arg in args:
        username_pattern = re.compile("^@.*")
        username_match = username_pattern.match(arg)

        if username_match:
            should_get_kicked.append(await client.get_entity(username_match.group(0)))
            continue

    try:    
        messages = await utils.get_replied_message(client, event)
        reply_sender = messages.sender
        should_get_kicked.append(reply_sender)
    except:
        pass

    chat = await client.get_entity(event.chat_id)
    permissions = await client.get_permissions(chat, 'me')

    tags =  []
    for user in should_get_kicked:
        if permissions.is_admin and not user.is_self:
            try:
                await client.kick_participant(entity=chat, user=user)
                tags.append(utils.tag_user(user))
            except:
                pass
    return f"Kicked {', '.join(tags)}"

async def random_int(**kwargs):
    args = kwargs["args"]
    return str(random.randint(int(args[0]),int(args[1])))

async def shell(**kwargs):
    args = kwargs["args"]
    return subprocess.run(" ".join(args), shell=True, capture_output=True, text=True).stdout

async def whogay(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    chat = await client.get_entity(event.chat_id)
    users_in_chat=await client.get_participants(chat)
    if users_in_chat.total == 1:
        users_in_chat.append(await client.get_me())
    user = random.choice(users_in_chat)
    return f"{utils.tag_user(user)} is gay af"

async def send_media(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    chat = await client.get_entity(event.chat_id)
    for path in args:
        try: 
            await client.send_file(chat, path)
        except:
            await client.send_file(chat, path, force_document=True)

async def send_file(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    chat = await client.get_entity(event.chat_id)
    for path in args:
        await client.send_file(chat, path, force_document=True)

    return None

async def shell_to_file(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    return await send_file(client=client, event=event, args=(await shell(args=args)).splitlines())

async def shell_to_media(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    return await send_media(client=client, event=event, args=(await shell(args=args)).splitlines())

async def instagram_add_dd(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    message = await utils.get_replied_message(client, event)
    chat = await client.get_entity(event.chat_id)
    await client.send_message(chat,message.message.replace("instagram", "ddinstagram"), reply_to=message)

async def everyone(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    chat = await client.get_entity(event.chat_id)
    return " ".join([utils.tag_user(user) for user in await client.get_participants(chat) if not user.bot and not user.is_self]+args)

async def tag_everyone(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]

    chat = await client.get_entity(event.chat_id)
    message = await utils.get_replied_message(client, event)
    tags = await everyone(client=client,event=event,args=args)
    try:
        await client.send_message(chat,tags, reply_to=message)
    except:
        await client.send_message(chat,tags)

async def eval_python(**kwargs):
    args = kwargs["args"]
    return str(eval(" ".join(args)))
    
async def exec_python(**kwargs):
    args = kwargs["args"]
    return str(exec(" ".join(args)))

async def parse_markdown(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    message = kwargs["message"]
    message = re.sub(r"^md\s", "",message, count=1)

    dict = {
            "name": "md",
            "lang": "en",
            }
    key_value_pattern = ".+=.+"
    key_values = re.findall(key_value_pattern, message)
    message = re.sub(key_value_pattern, '', message)

    for key_value in key_values:
        [key, value] = key_value.strip().split("=")
        dict[key] = value

    # add font config
    pre_message = f"""---
lang: {"ar" if dict["lang"]=="en" else "en"}
lang: ar
mainfont: Vazirmatn Regular
monofont: JetBrains Mono Regular
---
""" 

    pre_message += """\\newcommand{\\ar}{\\selectlanguage{arabic}}
\\newcommand{\\en}{\\selectlanguage{english}}
"""

    if dict["lang"]=="en":
        pre_message+='\\en\n'
    message = pre_message + message

    chat = await client.get_entity(event.chat_id)
    pdf_bytes = subprocess.run([ 'pandoc', '-f', 'markdown', '-t', 'pdf', '--pdf-engine', 'xelatex', '-o', '-' ], 
                          input=message.encode(),
                          stdout=subprocess.PIPE).stdout
    file = await client.upload_file(pdf_bytes, file_name=f"{dict['name']}.pdf")
    await client.send_file(chat, file, force_document=True)

async def string_times(**kwargs):
    args = kwargs["args"]
    client = kwargs["client"]
    event = kwargs["event"]
    message = kwargs["message"]
    message_to_times = " ".join(args[1:]).replace(r"\n","\n").replace(r"\s", " ");

    messages = (message_to_times*int(args[0])).split(r"\b")
    if len(messages) > 1:
        chat = await client.get_entity(event.chat_id)
        for message in messages:
            if message:
                await client.send_message(chat, message)
    else:
        return messages[0]

async def run_qalc(**kwargs):
    args = kwargs["args"]
    return subprocess.run(["qalc"]+args, capture_output=True, text=True).stdout

async def add_alias(**kwargs):
    args = kwargs["args"]
    functions_dict[args[0]] = " ".join(args[1:]).replace("\\","")

functions_dict = {
'kick': kick,
'rand':  random_int,
# 'shell':  shell, 
'rtfw': "https://wiki.archlinux.org",
'whogay': whogay,
'file': send_file,
'medi': send_media,
'alias': add_alias,
# 'shfile': shell_to_file,
# 'shmedi': shell_to_media,
'dd': instagram_add_dd,
'everyone': everyone,
'@everyone': tag_everyone,
# 'eval': eval_python,
# 'exec': exec_python,
'md': parse_markdown,
'qalc': run_qalc,
'times': string_times,
}

if __name__ == "__main__":
    main()
