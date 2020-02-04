#!/usr/bin/env python3
import signal
import os
import sys
import threading
import json
from bot import Bot
from groupy.client import Client
from time import sleep

bot_path = os.path.dirname(os.path.realpath(__file__))

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

'''
try:
    groups = os.environ['GROUPME_GROUPS'].split(" ")
    if len(groups) == 1:
        groups = groups[0].split(",")
    groups = list(filter(lambda x: x.strip() != "", groups))
    groups = list(map(lambda x: x.strip(), groups))
except KeyError:
    try:
        with open(os.path.abspath(bot_path + '/../groups.txt'), 'r') as bot_groups:
            for b in bot_groups.readlines():
                if b.strip()[:2] != "//":
                    groups.append(b.strip())
    except FileNotFoundError:
        print("Couldn't find  groups.txt. Make sure it is in the root of this directory")
        sys.exit(1)
'''

groups = {}

try:
    with open('groups.json') as allGroups:
        groups = json.load(allGroups)
except FileNotFoundError:
    potentialGroups = []
    for group in client.groups.list():
        potentialGroups.append((group.id, group.name))

    print("Which groups to use the bot for?")

    for index, pair in enumerate(potentialGroups):
        print("{}: {}".format(index + 1, pair[1]))

    choices = input("Which ones (comma separated): ").split(",")
    chosenGroups = {}
    for choice in choices:
        try:
            chosenGroups[potentialGroups[int(choice) - 1][1]] = potentialGroups[int(choice) - 1][0]
        except ValueError:
            pass
        except IndexError:
            pass

    with open('groups.json', 'w') as g:
        json.dump(chosenGroups, g)


def consume(bot, s=1):
    thread = threading.currentThread()
    while getattr(thread, "do_run", True):
        bot.process_message(bot.get_message())
        sleep(s)
    else:
        print("Stopping {} thread".format(thread.name))


client = Client.from_token(chat_key)

for g in groups:
    try:
        g = list(filter(lambda x: x.id == g, client.groups.list()))[0]
        b = Bot(g, yt_key=yt_key)
        print("creating thread for {}".format(g.name))
        threading.Thread(target=consume, name=g.name, daemon=True, args=(b, .1)).start()
    except IndexError:
        print("'{}' group doesn't exist".format(g))


def shutdown_bot(signal, frame):
    print("Shutting down the bot")
    for thread in threading.enumerate():
        if isinstance(thread, threading.Thread) and thread.name != "MainThread":
            thread.do_run = False
        if isinstance(thread, threading.Timer):
            thread.cancel()


signal.signal(signal.SIGINT, shutdown_bot)

print("Bot started up successfully")
