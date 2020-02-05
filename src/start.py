#!/usr/bin/env python3
import signal
import os
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

client = Client.from_token(chat_key)
groups = {}

try:
    with open(os.path.abspath(bot_path + '/../groups.json'), 'r') as all_groups:
        groups = json.load(all_groups)
except FileNotFoundError:
    potential_groups = []
    for group in client.groups.list():
        potential_groups.append((group.id, group.name))

    print("Which groups to use the bot for?")

    for index, pair in enumerate(potential_groups):
        print("{}: {}".format(index + 1, pair[1]))

    choices = input("Which ones (comma separated): ").split(",")
    chosen_groups = {}
    for choice in choices:
        try:
            chosen_groups[potential_groups[int(choice) - 1][1]] = {"id": potential_groups[int(choice) - 1][0], "enabled": True}
        except ValueError:
            pass
        except IndexError:
            pass

    with open(os.path.abspath(bot_path + 'groups.json'), 'w') as g:
        json.dump(chosen_groups, g, sort_keys=True, indent=2)
    groups = chosen_groups


def consume(bot, s=1):
    thread = threading.currentThread()
    while getattr(thread, "do_run", True):
        bot.process_message(bot.get_message())
        sleep(s)
    else:
        print("Stopping {} thread".format(thread.name))


for g in groups.values():
    try:
        if g['enabled']:
            g = client.groups.get(g['id'])
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
