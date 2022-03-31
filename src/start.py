#!/usr/bin/env python3
import argparse
import configparser
import discord
import json
import os
from remind import Remind
from tags import Tags
from utilities import Utilities

client = discord.Client()
ult = Utilities()
BOT_PATH = os.path.dirname(os.path.realpath(__file__))
delim = '$'
tags = {}
reminds = {}


async def ping(**kwargs):
    Utilities.log(f"ping kwargs: {kwargs}")
    return 'pong'


def parse_tag_commands(**kwargs):
    """
    **kwargs = {'args': ['just', datetime.datetime(2022, 3, 30, 23, 36, 27, 131000), 112784387862450176]}
        or
    **kwargs = {'args': ['filter', 'just', datetime.datetime(2022, 3, 30, 23, 40, 14, 616000), 112784387862450176, 224644073795878913]}
    """
    Utilities.log(f"parse_tag_commands kwargs: {kwargs}")
    # getting the Tag obj for that discord space
    tag = tags[kwargs['args'][-1]]
    args = kwargs['args'][:-1]
    del args[-2]  # deleting the datetime obj since it isn't used
    return tag.parse_commands(args=args)


def parse_remind_commands(**kwargs):
    """
    **kwargs = {'args': ['5m', 'clean', 'room',
                        <bound method Client.fetch_user of <discord.client.Client object at 0x7fb1c84fffd0>>,
                        datetime.datetime(2022, 3, 31, 0, 25, 49, 339000), 112784387862450176, 224644073795878913]
            }
    args[0] = time
    args[1:-4] = message
    args[-4] = discord function to get user name from user id
    args[-3] = time message was created
    args[-2] = user id
    args[-1] = discord channel id
    """
    Utilities.log(f"parse_remind_commands kwargs: {kwargs}")
    # getting the Remind obj for that discord space
    r = reminds[kwargs['args'][-1]]
    time = kwargs['args'][0]
    message = kwargs['args'][1:-4]
    fetch_user_func = kwargs['args'][-4]
    # can't convert the time given from discord to EST so I will
    # just use datetime to get the time that way
    # created_at = kwargs['args'][-3]
    created_at = None
    user = kwargs['args'][-2]
    return r.create_reminder(time, message, user, created_at, fetch_user_func)


def yt_search(**kwargs):
    Utilities.log(f"yt_search kwargs: {kwargs}")
    query = ' '.join(kwargs['args'][:-2])
    return ult.yt_search(query)


def mock(**kwargs):
    Utilities.log(f"mock kwargs: {kwargs}")
    message = ' '.join(kwargs['args'][:-2])
    return Utilities.mock(message)


def git(**kwargs):
    return Utilities.git()


valid_commands = {
    'ping': ping,
    'tag': parse_tag_commands,
    'yt': yt_search,
    'git': git,
    'mock': mock,
    'remind': parse_remind_commands
}


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}\n")
    print("server - server id - channel - channel id\n=========================================")
    for channel in client.get_all_channels():
        if str(channel.category) == 'Text Channels':
            print(f"Text Channel: {channel.guild} - {channel.guild.id} - {channel} - {channel.id}")
            tag_json_path = os.path.abspath(f"{BOT_PATH}/../tags")
            reminders_json_path = os.path.abspath(f"{BOT_PATH}/../reminders")
            if channel.guild.id not in tags:
                tags[channel.guild.id] = Tags(channel.guild, tag_json_path)
            if channel.guild.id not in reminds:
                reminds[channel.guild.id] = Remind(channel.guild, reminders_json_path, client)
    print('Initializing Done')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(delim):
        command = message.content[1:].split(" ")
        print(f"command: {command}")
        if command[0] in valid_commands:
            # print(message)
            args = command[1:]
            if message.attachments:
                args.append(message.attachments[0].url)
            if (command[0] == 'remind') or (command[0] == 'tag' and args[0] == 'owner'):
                args.append(client.fetch_user)
            args.append(message.created_at)
            args.append(message.author.id)
            args.append(message.channel.guild.id)
            command = command[0]
            result = await valid_commands[command](args=args)
            await message.channel.send(result)


def main():
    config_parser = configparser.ConfigParser()

    parser = argparse.ArgumentParser(description="groupme bot")
    parser.add_argument("-c", "--config", help="ini file containing keys and other bot info", type=str, required=True)
    args = parser.parse_args()

    config_parser.read(os.path.abspath(args.config))
    if 'youtube' in config_parser['keys']:
        ult.set_yt_key(config_parser['keys']['youtube'])
    client.run(config_parser['keys']['discord'])


if __name__ == '__main__':
    main()

