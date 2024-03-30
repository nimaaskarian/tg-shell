#!/bin/python3
import subprocess, random, json, re, math, io
from http.client import HTTPConnection

from telethon import events
import os
from telethon.sync import TelegramClient

import pathlib
dir = pathlib.Path(__file__).parent.resolve()

import utils
import sys
proxy = None
try:
    connection = HTTPConnection("telegram.org", port=80, timeout=1)
    connection.request("HEAD", "/")
except:
    proxy =("socks5", '127.0.0.1', 2080)

creds_file = open(os.path.join(dir,"credentials.json"))
creds = json.load(creds_file)

def main():
    with TelegramClient( os.path.join(dir,creds["name"]), creds["api_id"], creds["api_hash"], proxy=proxy) as client: 
        print("Ok")
        for id in sys.argv[1].split():
            chat = client.get_entity(id)

            client.send_message(chat,sys.argv[2])

if __name__ == "__main__":
    main()
