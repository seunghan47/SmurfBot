#!/usr/bin/env python3
"""Sets up and initializes the bot"""
import signal
import os
import sys
import threading
import json
import configparser
from time import sleep
from groupy.client import Client
from bot import Bot

BOT_PATH = os.path.dirname(os.path.realpath(__file__))


def main():
    """
    :return: sets up the groups the bot will listen and then initialize the threads
    """
    parser = configparser.ConfigParser()
    parser.read("config.ini")
    try:
        chat_key = parser['keys']['groupme']
    except KeyError:
        print("Need groupme api key to continue")
        sys.exit(1)

    try:
        yt_key = parser['keys']['youtube']
    except KeyError:
        yt_key = None

    delim = parser['bot']['delim']
    refresh_group_interval = int(parser['bot']['refresh_group_interval'])
    consume_time = float(parser['bot']['consume_time'])

    client = Client.from_token(chat_key)
    groups = {}

    try:
        with open(os.path.abspath(BOT_PATH + '/../groups.json'), 'r') as all_groups:
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
                chosen_groups[potential_groups[int(choice) - 1][1]] = {"id": potential_groups[int(choice) - 1][0],
                                                                       "enabled": True}
            except ValueError:
                pass
            except IndexError:
                pass

        with open(os.path.abspath(BOT_PATH + '/../groups.json'), 'w') as finalized_groups:
            json.dump(chosen_groups, finalized_groups, sort_keys=True, indent=2)
        groups = chosen_groups

    for group in groups.values():
        try:
            if group['enabled']:
                group = client.groups.get(group['id'])
                bot = Bot(group, yt_key=yt_key, delim=delim, refresh_group_interval=refresh_group_interval)
                print("creating thread for {}".format(group.name))
                threading.Thread(target=consume, name=group.name, daemon=True, args=(bot, consume_time)).start()
        except IndexError:
            print("'{}' group doesn't exist".format(group))

    signal.signal(signal.SIGINT, shutdown_bot)

    print("Bot started up successfully")


def consume(bot, seconds=1):
    """
    :param bot: Bot object that contains group and yt_key
    :param seconds: units in seconds that the parsing of messages will pause after each parsing
    :return: either will process the messages and if a command is present, it'll post in the group chat forever.
    also checks to see if thread should continue to run or end
    """
    thread = threading.currentThread()
    while getattr(thread, "do_run", True):
        bot.process_message(bot.get_message())
        sleep(seconds)
    print("Stopping {} thread".format(thread.name))


def shutdown_bot(s, f):
    """
    :return: gracefully terminates the child threads and timers
    """
    print("Shutting down the bot")
    for thread in threading.enumerate():
        if isinstance(thread, threading.Thread) and thread.name != "MainThread":
            thread.do_run = False
        if isinstance(thread, threading.Timer):
            thread.cancel()


if __name__ == '__main__':
    main()
