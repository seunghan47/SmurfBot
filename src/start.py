#!/usr/bin/env python3
"""Sets up and initializes the bot"""
import argparse
import signal
import os
import sys
import threading
import json
import configparser
import groupy.exceptions
import requests.exceptions
from time import sleep
from groupy.client import Client
from bot import Bot
from datetime import datetime

BOT_PATH = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description="groupme bot")
parser.add_argument("-c", "--config", help="ini file containing keys and other bot info", type=str, required=True)
parser.add_argument("-g", "--groups", help="json file with the groups the bot will listen to", type=str, required=True)


def get_current_datetime():
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S")


def main():
    """
    :return: sets up the groups the bot will listen and then initialize the threads
    """
    args = parser.parse_args()
    config_parser = configparser.ConfigParser()
    config_path = os.path.abspath(args.config)
    config_parser.read(config_path)
    try:
        chat_key = config_parser['keys']['groupme']
    except KeyError:
        print("{} - Need groupme api key to continue".format(get_current_datetime()))
        sys.exit(1)

    try:
        yt_key = config_parser['keys']['youtube']
    except KeyError:
        yt_key = None

    delim = config_parser['bot']['delim']
    refresh_group_interval = int(config_parser['bot']['refresh_group_interval'])
    consume_time = float(config_parser['bot']['consume_time'])

    client = Client.from_token(chat_key)
    groups = {}

    try:
        with open(os.path.abspath(args.groups), 'r') as all_groups:
            groups = json.load(all_groups)
    except FileNotFoundError:
        potential_groups = []
        group_file_path = os.path.abspath(args.groups)
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

        with open(os.path.abspath(group_file_path), 'w') as finalized_groups:
            json.dump(chosen_groups, finalized_groups, sort_keys=True, indent=2)
            print("created groups.json at {}".format(group_file_path))
        groups = chosen_groups
    for group in groups:
        name = group
        group = groups[group]
        try:
            if group['enabled']:
                group = client.groups.get(group['id'])
                bot = Bot(group, yt_key=yt_key, delim=delim, refresh_group_interval=refresh_group_interval)
                print("{} - creating thread for {}".format(get_current_datetime(), group.name))
                threading.Thread(target=consume, name=group.name, daemon=True, args=(bot, consume_time)).start()
        except (IndexError, groupy.exceptions.BadResponse, requests.exceptions.HTTPError):
            print("{} - '{}' group doesn't exist".format(get_current_datetime(), name))

    signal.signal(signal.SIGINT, shutdown_bot)

    print("{} - Bot started up successfully".format(get_current_datetime()))


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
    print("{} - {}: Stopping {} thread".format(get_current_datetime(), bot.group.name, thread.name))


def shutdown_bot(s, f):
    """
    :return: gracefully terminates the child threads and timers
    """
    print("{} - Shutting down the bot".format(get_current_datetime()))
    for thread in threading.enumerate():
        if isinstance(thread, threading.Thread) and thread.name != "MainThread":
            thread.do_run = False
        if isinstance(thread, threading.Timer):
            thread.cancel()


if __name__ == '__main__':
    main()
