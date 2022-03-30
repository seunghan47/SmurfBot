import json
import os

from atomicwrites import atomic_write
from utilities import Utilities


class Remind:
    def __init__(self, guild, reminders_json_path):

        self.guild = guild
        self.reminders_json_path = reminders_json_path
        self.reminders_json_file = f"{reminders_json_path}/{guild.id}.json"
        self.reminders = self.load_reminders()

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

    async def create_reminder(self, time, message, user):
        self.reminders['reminders'].append({
            'user': user,
            'time': time,
            'message': message
        })
        self.save_reminders()
        return f"Created reminder for {user} at {time}"
