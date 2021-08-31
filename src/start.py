#!/usr/bin/env python3
import argparse
import configparser
import discord
import json
import os
from tags import Tags
from utilities import Utilities

client = discord.Client()
ult = Utilities()
BOT_PATH = os.path.dirname(os.path.realpath(__file__))
delim = '$'
tags = {}


def ping(**kwargs):
    print(kwargs)
    return 'pong'


def parse_tag_commands(**kwargs):
    Utilities.log(f"parse_tag_commands kwargs: {kwargs}")
    tag = tags[kwargs['args'][-1]]
    args = kwargs['args'][:-1]
    return tag.parse_commands(args=args)


def yt_search(**kwargs):
    query = ' '.join(kwargs['args'][:-1])
    return ult.yt_search(query)


valid_commands = {
    'ping': ping,
    'tag': parse_tag_commands,
    'yt': yt_search
}


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}\n")
    print("server - server id - channel - channel id\n=========================================")
    for channel in client.get_all_channels():
        if str(channel.category) == 'Text Channels':
            print(f"Text Channel: {channel.guild} - {channel.guild.id} - {channel} - {channel.id}")
            tag_json_path = os.path.abspath(f"{BOT_PATH}/../tags")
            if channel.guild.id not in tags:
                tags[channel.guild.id] = Tags(channel.guild, tag_json_path)
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
            args.append(message.author.id)
            args.append(message.channel.guild.id)
            command = command[0]
            result = valid_commands[command](args=args)
            await message.channel.send(result)
        else:
            await message.channel.send(f"{command} isn't a valid command")


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

