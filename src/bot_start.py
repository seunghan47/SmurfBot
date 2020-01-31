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

client = Client.from_token(chat_key)

# Use this for loop to find groups you want
for g in client.groups.list():
    if g.name == 'ddgbot test':
        test_group = g
    if g.name == 'Smurf City Pt 2':
        smurf_city = g
    if g.name == 'Couch':
        house_hunters = g

# make a bot object for each group you want
smurf_city_bot = Bot(smurf_city, yt_key=yt_key)
test_group_bot = Bot(test_group, yt_key=yt_key)
house_hunters_bot = Bot(house_hunters, yt_key=yt_key)


def shutdown_bot(signal, frame):
    print("Shutting down the bot")
    smurf_city_bot.save_tags()
    test_group_bot.save_tags()
    house_hunters_bot.save_tags()
    sys.exit(0)


def tag_reloader(signal, frame):
    print("reloading tags")
    smurf_city_bot.reload_tags()
    test_group_bot.reload_tags()
    house_hunters_bot.reload_tags()


signal.signal(signal.SIGINT, shutdown_bot)
signal.signal(signal.SIGQUIT, tag_reloader)

print("Bot started up successfully")


# make a method for each group
def test_group():
    while True:
        message = test_group_bot.get_message()
        test_group_bot.process_message(message)
        sleep(1)
        

def smurf_group():
    while True:
        message = smurf_city_bot.get_message()
        smurf_city_bot.process_message(message)
        sleep(.1)


def house_group():
    while True:
        message = house_hunters_bot.get_message()
        house_hunters_bot.process_message(message)
        sleep(.1)


# add a threading method for each group
threading.Thread(target=test_group, daemon=True).start()
threading.Thread(target=smurf_group, daemon=True).start()
threading.Thread(target=house_group, daemon=True).start()
