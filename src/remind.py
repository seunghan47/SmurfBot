import asyncio
import json
import os
import pytz

from atomicwrites import atomic_write
from datetime import datetime, timedelta
from utilities import Utilities


class Remind:
    def __init__(self, guild, reminders_json_path, client):

        self.guild = guild
        self.reminders_json_path = reminders_json_path
        self.reminders_json_file = f"{reminders_json_path}/{guild.id}.json"
        self.reminders = self.load_reminders()
        self.channel = client.get_channel(self.guild.id)
        self.date_format = '%Y-%m-%dT%H:%M:%S'
        self.loop = client.loop
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

    def parse_time(self, time):
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

    async def parse_reminders(self):
        for reminder in self.reminders['reminders']:
            await self.parse_reminder(reminder)

    async def parse_reminder(self, reminder):
        current_datetime = datetime.now(pytz.timezone('US/Eastern'))
        planned_execution_date = datetime.strptime(reminder['created_at'], self.date_format) + timedelta(seconds=remainder['time'])

        if planned_execution_date > current_datetime:
            time_difference = (planned_execution_date - current_datetime).total_seconds()
            await self.send_message(reminder['message'], reminder['user_id'], time_difference)

    async def send_message(self, message, user_id, seconds):
        await asyncio.sleep(seconds)
        await self.channel.send(f"<@{user_id}> reminder: {message}")

    async def create_reminder(self, time, message, user_id, created_at, fetch_user):
        user = await fetch_user(user_id)
        time = self.parse_time(time)
        message = " ".join(message)
        created_at = datetime.now(pytz.timezone('US/Eastern'))
        self.reminders['reminders'].append({
            'user_id': user_id,
            'name': user.name,
            'time': time,
            'message': message,
            'created_at': created_at.strftime(self.date_format)
        })
        self.save_reminders()
        execution_time = (created_at + timedelta(seconds=time)).strftime('%m/%d/%Y @ %I:%M:%S%p')
        asyncio.run_coroutine_threadsafe(self.send_message(message, user_id, time), self.loop)
        return f"Created reminder for {user.name} to go off at {execution_time}"
