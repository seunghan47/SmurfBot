#!/usr/bin/env python3
import signal
import os
import sys
import threading
from bot import Bot
from groupy.client import Client
from time import sleep

bot_path = os.path.dirname(os.path.realpath(__file__))
groups = []

try:
    chat_key = os.environ['GROUPME_KEY']
except KeyError:
    with open(os.path.abspath(bot_path + '/../creds/groupme.key'), 'r') as groupme_key:
        chat_key = groupme_key.readline().strip()

try:
    yt_key = os.environ['YT_KEY']
except KeyError:
    try:
        with open(os.path.abspath(bot_path + '/../creds/youtube_api.key'), 'r') as yt_key:
            yt_key = yt_key.readline().strip()
    except FileNotFoundError:
        yt_key = None

try:
    with open(os.path.abspath(bot_path + '/../groups.txt'), 'r') as bot_groups:
        groups = bot_groups.readlines()
except FileNotFoundError:
    print("Couldn't find  groups.txt. Make sure it is in the root of this directory")
    sys.exit(1)

client = Client.from_token(chat_key)


def consume(bot, s=1):
    thread = threading.currentThread()
    while getattr(thread, "do_run", True):
        bot.process_message(bot.get_message())
        sleep(s)
    else:
        print("Stopping {} thread".format(thread.name))


for g in groups:
    try:
        g = list(filter(lambda x: x.name == g.strip(), client.groups.list()))[0]
        b = Bot(g, yt_key=yt_key)
        threading.Thread(target=consume, name=g.name, daemon=True, args=(b, .1)).start()
    except IndexError:
        print("'{}' group doesn't exist".format(g))


def shutdown_bot(signal, frame):
    print("Shutting down the bot")
    print(threading.enumerate())
    for thread in threading.enumerate():
        if isinstance(thread, threading.Thread) and thread.name != "MainThread":
            thread.do_run = False
        if isinstance(thread, threading.Timer):
            thread.cancel()


signal.signal(signal.SIGINT, shutdown_bot)

print("Bot started up successfully")
