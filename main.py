#!/bin/python3

import time
import subprocess, random, json, re, math, io
from http.client import HTTPConnection
from telethon.tl.types import InputMediaPoll, PollAnswer
from telethon import functions
from telethon import functions, types

from telethon import events
import os
from telethon.sync import TelegramClient

import utils

proxy = None
try:
    connection = HTTPConnection("telegram.org", port=80, timeout=1)
    connection.request("HEAD", "/")
except:
    proxy =("socks5", '127.0.0.1', 40000)

import pathlib
dir = pathlib.Path(__file__).parent.resolve()
creds_file = open(os.path.join(dir,"credentials.json"))
creds = json.load(creds_file)

def main():
    with TelegramClient( os.path.join(dir,creds["name"]), creds["api_id"], creds["api_hash"], proxy=proxy) as client: 
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

async def get_entities(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    output = []
    if event.message.entities:
        for entity in event.message.entities:
            id_pattern = re.compile(r"tg://user\?id=\d+")

            try:
                id_match = id_pattern.match(entity.url)
            except:
                continue
            if id_match:
                output.append(await client.get_entity(int(id_match.group(0).replace("tg://user?id=", ""))))

    for arg in args:
        username_pattern = re.compile("^@.*")
        username_match = username_pattern.match(arg)

        if username_match:
            output.append(await client.get_entity(username_match.group(0)))
            continue

    try:    
        messages = await utils.get_replied_message(client, event)
        reply_sender = messages.sender
        output.append(reply_sender)
    except:
        pass

    return output
async def everyone_print(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    chat = await client.get_entity(event.chat_id)
    for user in await client.get_participants(chat):
        print(user)


async def kick(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]

    chat = await client.get_entity(event.chat_id)

    permissions = await client.get_permissions(chat, 'me')
    tags =  []
    for user in await get_entities(client=client, event=event, args=args):
        if permissions.is_admin and not user.is_self:
            try:
                await client.kick_participant(entity=chat, user=user)
                tags.append(utils.tag_user(user))
            except:
                pass
    if tags:
        return f"Kicked {', '.join(tags)}"

async def ban(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]

    chat = await client.get_entity(event.chat_id)

    permissions = await client.get_permissions(chat, 'me')
    tags =  []
    for user in await get_entities(client=client, event=event, args=args):
        if permissions.is_admin and not user.is_self:
            try:
                await client.edit_permissions(chat, user, view_messages=False)
                tags.append(utils.tag_user(user))
            except:
                pass
    if tags:
        return f"Banned {', '.join(tags)}"

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

async def get_tags(chat, client):
    return [utils.tag_user(user) for user in await client.get_participants(chat) if not user.bot and not user.is_self]

async def everyone(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    chat = await client.get_entity(event.chat_id)
    return " ".join(await get_tags(chat,client))

async def tag_everyone(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]

    chat = await client.get_entity(event.chat_id)
    message = await utils.get_replied_message(client, event)
    tags = await get_tags(chat, client)
    print(tags)
    n = 5
    for list in [tags[i * n:(i + 1) * n] for i in range((len(tags) + n - 1) // n )]:
        if len(list):
            send = " ".join(list)
            try:
                await client.send_message(chat,send, reply_to=message)
            except:
                await client.send_message(chat,send)


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
    functions_dict[args[0]] = " ".join(args[1:]).replace(r"\```","```")

async def persian_to_english_numbers(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    persian_numbers = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9'
    }
    message = await utils.get_replied_message(client, event)
    
    english_string = ""
    
    for char in message.message:
        if char in persian_numbers:
            english_string += persian_numbers[char]
        else:
            english_string += char
    
    return english_string

async def fix_keyboard_layout_misstype(**kwargs):
    pass

async def repeat_message(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    chat = await client.get_entity(event.chat_id)

    await client.delete_messages(chat, [event.message])
    message = await utils.get_replied_message(client, event)
    str_to_repeat = message.message

    async def till_stop(message):
        if len(args) > 1 and int(args[1]) == 1:
            result = await client(functions.messages.GetPeerDialogsRequest(peers=[chat]))
            return result.dialogs[0].read_outbox_max_id < message.id
        else:
            return True

    while await till_stop(message):
        await client.delete_messages(chat, [message])
        message = await client.send_message(chat, str_to_repeat)
        time.sleep(int(args[0]))

async def times_cmd(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    args = kwargs["args"]
    message = await utils.get_replied_message(client, event)

    for i in range(int(args[0])):
        command = functions_dict[args[1]]
        await command(
                    client=client,
                    event=event,
                    args=args[2:],
                    message=message,
                    )

async def username_to_id(**kwargs):
    client = kwargs["client"]
    # event = kwargs["event"]
    args = kwargs["args"]
    # message = kwargs["message"]
    chat = await client.get_entity(args[0])
    return str(chat.id)

async def dislike_message(message, client, chat):
    await client(functions.messages.SendReactionRequest(
        peer=chat,
        msg_id=message.id,
        big=True,
        add_to_recent=True,
        reaction=[types.ReactionEmoji(
            emoticon='👎'
        )]
    ))

async def dislike_replied_user_messages(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    chat = await client.get_entity(event.chat_id)
    message = await utils.get_replied_message(client, event)
    async for message in client.iter_messages(chat, from_user=message.from_id):
        await dislike_message(message, client, chat)

async def dislike(**kwargs):
    client = kwargs["client"]
    event = kwargs["event"]
    message = await utils.get_replied_message(client, event)
    chat = await client.get_entity(event.chat_id)
    await dislike_message(message, client, chat)

async def save_replies_in_file(**kwargs):
    pass

async def delete_up(**kwargs):
    event = kwargs["event"]
    client = kwargs["client"]
    chat = await client.get_entity(event.chat_id)
    args = kwargs["args"]
    delete_count = int(args[0])
    try:
        ignore_first = int(args[0])
    except:
        ignore_first = 1

    async for message in client.iter_messages(chat):
        if ignore_first:
            ignore_first-=1
            continue

        if delete_count == 0:
            break
        await client.delete_messages(chat, [message])
        delete_count -= 1




functions_dict = {
'kick': kick,
'rand':  random_int,
# 'shell':  shell, 
'rtfw': "https://wiki.archlinux.org",
'whogay': whogay,
'file': send_file,
'medi': send_media,
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
'alias': add_alias,
'ban': ban,
'print': everyone_print,
'eng': persian_to_english_numbers,
'rep': repeat_message,
'timescmd': times_cmd,
'whois': username_to_id,
'dislike': dislike,
'grabrep': save_replies_in_file,
'del': delete_up,
'dislikeall': dislike_replied_user_messages,
}

if __name__ == "__main__":
    main()
