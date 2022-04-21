import asyncio
import json
import pytz
import os

from atomicwrites import atomic_write
from datetime import datetime, timedelta, timezone
from utilities import Utilities

date_format = '%Y-%m-%dT%H:%M:%S'
human_date_format = '%m/%d/%Y @ %I:%M:%S%p'


def parse_time(time):
    unit = time[-1]
    amount = int(time[:-1])
    match unit:
        case 's':
            pass
        case 'm':
            amount = amount * 60
        case 'h':
            amount = amount * 60 * 60
        case 'd':
            amount = amount * 60 * 60 * 24
        case _:
            amount = None
    return amount


def add_time_to_date(date, seconds):
    if type(date) == str:
        date = datetime.strptime(date, date_format).replace(tzinfo=timezone.utc)
    return date + timedelta(seconds=seconds)


def has_datetime_passed(planned_execution_date):
    current_datetime = datetime.now(timezone.utc)
    if type(planned_execution_date) is str:
        planned_execution_date = datetime.strptime(planned_execution_date, date_format).replace(tzinfo=timezone.utc)
    Utilities.log(f"has_datetime_passed() - current_datetime: ({type(current_datetime)}) {current_datetime} {current_datetime.tzinfo}")
    Utilities.log(f"has_datetime_passed() - planned_execution_date: ({type(planned_execution_date)}) {planned_execution_date} {planned_execution_date.tzinfo}")
    if planned_execution_date > current_datetime:
        Utilities.log(f"has_datetime_passed() - seconds_until_execution: {(planned_execution_date - current_datetime)}")
        Utilities.log(f"has_datetime_passed() - seconds_until_execution.total_seconds(): {(planned_execution_date - current_datetime).total_seconds()}")
        return {'result': False, 'seconds_until_execution': (planned_execution_date - current_datetime).total_seconds()}
    Utilities.log(f"has_datetime_passed() - {planned_execution_date} has passed")
    return {'result': True, 'seconds_until_execution': -1}


class Remind:
    def __init__(self, guild, reminders_json_path, client):
        self.guild = guild
        self.reminders_json_path = reminders_json_path
        self.reminders_json_file = f"{reminders_json_path}/{guild.id}.json"
        self.reminders = self.load_reminders()
        self.loop = client.loop
        self.clean_reminders()
        asyncio.run_coroutine_threadsafe(self.parse_reminders(), self.loop)

    def create_json(self):
        """
        :return: creates the tags directory if it doesn't exist. creates the tags json file for the group
        if it doesn't exist
        """
        if not os.path.exists(self.reminders_json_path):
            os.makedirs(self.reminders_json_path)
            Utilities.log(f"created {self.reminders_json_path}")
        # creates reminders json file for the group if it doesn't exist
        if not os.path.exists(self.reminders_json_file):
            create_json = {'name': self.guild.name, 'id': self.guild.id, 'reminders': []}
            with open(self.reminders_json_file, 'w') as tags:
                json.dump(create_json, tags)
            Utilities.log(f"{self.guild.name}: created: {self.reminders_json_file}")

    def load_reminders(self):
        """
        :return: dictionary of the group's tag json file
        """
        self.create_json()
        Utilities.log(f"{self.guild.name}: loading: {self.reminders_json_file}")
        with open(self.reminders_json_file, 'r') as reminders:
            return json.load(reminders)

    def save_reminders(self):
        """
        :return: dumps the group's tag to the disk
        """
        Utilities.log(f"{self.guild.name}: saving: {self.reminders_json_file}")
        with atomic_write(self.reminders_json_file, overwrite=True) as reminders_file:
            reminders_file.write(json.dumps(self.reminders, sort_keys=True, indent=2))

    def clean_reminders(self):
        Utilities.log(f"{self.guild.name}: cleaning: {self.reminders_json_file}")
        self.reminders['reminders'] = list(filter(lambda x: has_datetime_passed(x['execution_time'])['result'] is False, self.reminders['reminders']))
        self.save_reminders()

    def list_reminders(self):
        self.clean_reminders()
        message = ''
        for reminder in self.reminders['reminders']:
            date = reminder['execution_time']
            if type(date) is str:
                Utilities.log('date is a string')
                date = datetime.strptime(date, date_format)

            date = datetime.astimezone(timezone.utc)
            Utilities.log(f"date timezone before conversion: {date.tzinfo}")
            date = date.astimezone(pytz.timezone('US/Eastern'))
            Utilities.log(f"date timezone after conversion: {date.tzinfo}")
            date = date.strftime(human_date_format)
            message = f"{message}\nCreated by: {reminder['name']}\nReminder date: {date}\nReminder message: {reminder['message']}\n"
        if message == '':
            return 'No active reminds were found'
        return message

    async def parse_reminders(self):
        Utilities.log(f"{self.guild.name}: parse_reminders()")
        Utilities.log(f"{self.guild.name}: {self.reminders}")
        for reminder in self.reminders['reminders']:
            await self.parse_reminder(reminder)

    async def parse_reminder(self, reminder):
        Utilities.log(f"{self.guild.name}: parse_reminder()")
        r = has_datetime_passed(reminder['execution_time'])
        if not r['result']:
            self.create_timer(reminder['message'], reminder['user_id'], reminder['name'], r['seconds_until_execution'], reminder['channel_id'])
        else:
            Utilities.log(f"{self.guild.name}: parse_reminder() - reminder for {reminder['name']} that says {reminder['message']} alredy expired")

    def create_timer(self, message, user_id, user_name, time, channel_id):
        asyncio.run_coroutine_threadsafe(self.send_message(message, user_id, time, channel_id), self.loop)
        Utilities.log(f"{self.guild.name}: created timer for {user_name} that will execute in {time} seconds")

    async def send_message(self, message, user_id, seconds, channel_id):
        await asyncio.sleep(seconds)
        channel = self.guild.get_channel(channel_id)
        await channel.send(f"<@{user_id}> reminder: {message}")

    async def create_reminder(self, seconds, message, user_id, created_at, fetch_user, guild_id, channel_id):
        user = await fetch_user(user_id)
        match seconds:
            case 'help':
                return 'Format: $remind [amount of time] [message]. Example: $remind 1h check laundry\nSupport units: '\
                       's (seconds), m (minutes), h (hours), or d (days). '
            case 'list':
                return self.list_reminders()
            case _:
                seconds = parse_time(seconds)
        if seconds is None:
            return f"Unsupported unit of time. Please use s (seconds), m (minutes), h (hours), or d (days)"
        message = " ".join(message)
        created_at = datetime.now(timezone.utc)
        self.reminders['reminders'].append({
            'user_id': user_id,
            'name': user.name,
            'message': message,
            'created_at': created_at.strftime(date_format),
            'execution_time': add_time_to_date(created_at, seconds).strftime(date_format),
            'timezone': 'utc',
            'guild_id': guild_id,
            'channel_id': channel_id
        })
        self.save_reminders()
        execution_time = (created_at + timedelta(seconds=seconds)).astimezone(pytz.timezone('US/Eastern')).strftime(human_date_format)
        self.create_timer(message, user_id, user.name, seconds, channel_id)
        return f"Created reminder for {user.name} to go off at {execution_time} that says `{message}`"
