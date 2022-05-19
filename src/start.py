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


async def ping(parameters):
    Utilities.log(f"ping parameters: {parameters}")
    return 'pong'


async def boob(parameters):
    return 'https://cdn.discordapp.com/attachments/224644073795878913/966783811641827438/timetostop.gif'


def parse_tag_commands(parameters):
    Utilities.log(f"parse_tag_commands parameters: {parameters}")
    # getting the Tag obj for that discord space
    tag = tags[parameters['guild_id']]
    return tag.parse_commands(parameters)


def parse_remind_commands(parameters):
    Utilities.log(f"parse_remind_commands parameters: {parameters}")
    channel_id = parameters['channel_id']
    guild_id = parameters['guild_id']
    # getting the Remind obj for that discord space
    r = reminds[guild_id]
    time = parameters['message'][0]
    message = parameters['message'][1:]
    fetch_user_func = parameters['fetch_user_func']
    created_at = None  # can't convert the time given from discord to EST so I will just use datetime.now()
    user = parameters['author_id']
    return r.create_reminder(time, message, user, created_at, fetch_user_func, guild_id, channel_id)


def yt_search(parameters):
    Utilities.log(f"yt_search parameters: {parameters}")
    query = ' '.join(parameters['message'])
    return ult.yt_search(query)


def mock(parameters):
    Utilities.log(f"mock parameters: {parameters}")
    message = ' '.join(parameters['message'])
    return Utilities.mock(message)


def git(parameters):
    return Utilities.git()


valid_commands = {
    'ping': ping,
    'tag': parse_tag_commands,
    'yt': yt_search,
    'git': git,
    'mock': mock,
    'remind': parse_remind_commands,
    'boob': boob
}


@client.event
async def on_ready():
    Utilities.log(f"We have logged in as {client.user}\n")
    Utilities.log(f"server - server id - channel - channel id\n=========================================")
    for channel in client.get_all_channels():
        if str(channel.category) == 'Text Channels':
            Utilities.log(f"Text Channel: {channel.guild} - {channel.guild.id} - {channel} - {channel.id}")
            tag_json_path = os.path.abspath(f"{BOT_PATH}/../tags")
            reminders_json_path = os.path.abspath(f"{BOT_PATH}/../reminders")
            if channel.guild.id not in tags:
                tags[channel.guild.id] = Tags(channel.guild, tag_json_path)
            if channel.guild.id not in reminds:
                reminds[channel.guild.id] = Remind(channel.guild, reminders_json_path, client)
    Utilities.log(f"Initializing Done")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith(delim):
        command = message.content[1:].split(" ")
        Utilities.log(f"command: {command}")
        if command[0] in valid_commands:
            parameters = {'command': command[0], 'message': command[1:], 'attachment': None}
            if message.attachments:
                parameters['attachment'] = message.attachments[0].url
            if (parameters['command'] == 'remind') or (parameters['command'] == 'tag' and parameters['message'][0] == 'owner'):
                parameters['fetch_user_func'] = client.fetch_user
            parameters['created_at'] = message.created_at
            parameters['author_id'] = message.author.id
            parameters['guild_id'] = message.channel.guild.id
            parameters['channel_id'] = message.channel.id

            command = command[0]
            result = await valid_commands[command](parameters)
            if len(command) == 2 and command[0] == 'tag' and command[1] == 'frfr':
                await message.delete()
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
