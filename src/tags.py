"""Handles all the tag related commands"""
import json
import os
from functools import reduce
from itertools import zip_longest

import discord
from atomicwrites import atomic_write
from utilities import Utilities


class Tags:
    """Handles all the tag related commands"""
    def __init__(self, guild, tags_json_path):
        self.guild = guild
        self.tags_json_path = tags_json_path
        self.tags_json_file = f"{tags_json_path}/{guild.id}.json"
        self.tags = self.load_tags()

    @staticmethod
    def post_help():
        """
        :return: string with details about the tag commands
        """
        return 'To create a tag: "tag create [name]" while uploading a picture or by providing a link or text after ' \
               'the name. To post an already created tag: \"tag [name]\". To see what tags are made: \"tag list\".' + \
               ' To edit a tag: \"tag edit [name] [new material]\". To rename a tag:\"tag rename [current name]' + \
               ' [new name]\".'

    def create_json(self):
        """
        :return: creates the tags directory if it doesn't exist. creates the tags json file for the group
        if it doesn't exist
        """
        if not os.path.exists(self.tags_json_path):
            os.makedirs(self.tags_json_path)
            Utilities.log(f"created {self.tags_json_path}")
        # creates tag json file for the group if it doesn't exist
        if not os.path.exists(self.tags_json_file):
            create_json = {'name': self.guild.name, 'id': self.guild.id, 'tags': {}}
            with open(self.tags_json_file, 'w') as tags:
                json.dump(create_json, tags)
            Utilities.log(f"{self.guild.name}: created: {self.tags_json_file}")

    def load_tags(self):
        """
        :return: dictionary of the group's tag json file
        """
        self.create_json()
        Utilities.log(f"{self.guild.name}: loading: {self.tags_json_file}")
        with open(self.tags_json_file, 'r') as tags:
            return json.load(tags)

    def save_tags(self):
        """
        :return: dumps the group's tag to the disk
        """
        Utilities.log(f"{self.guild.name}: saving: {self.tags_json_file}")
        with atomic_write(self.tags_json_file, overwrite=True) as tag_file:
            tag_file.write(json.dumps(self.tags, sort_keys=True, indent=2))

    def parse_commands(self, **kwargs):
        print(f"tags parse_commands kwargs: {kwargs}")
        message = kwargs['args']
        command = message[0].rstrip()
        tag_result = ''
        if command == "create":
            tag_result = self.create_tag(kwargs['args'][1], ' '.join(kwargs['args'][2: -1]), kwargs['args'][-1])
        elif command == "delete":
            tag_result = self.delete_tag(kwargs['args'][1], kwargs['args'][2])
        elif command == "list":
            tag_result = self.list_tags()
        elif command == "help":
            tag_result = self.post_help()
        elif command == "edit":
            pass
        elif command == "rename":
            pass
        elif command == "gift":
            pass
        elif command == "owner":
            tag_result = self.find_owner(kwargs['args'][1], kwargs['args'][2])
        elif command == "filter":
            tag_result = self.filter_tags(kwargs['args'][1])
        else:
            tag_result = self.post_tag(command.strip())

        return tag_result

    async def create_tag(self, name, content, owner):
        if name in self.tags['tags']:
            return f"The tag \"{name}\" already exists"
        self.tags['tags'][name] = {'owner': owner, 'content': content}
        self.save_tags()
        return f"The tag \"{name}\" was created successfully"

    async def post_tag(self, name):
        if name in self.tags['tags']:
            return self.tags['tags'][name]['content']
        return f"The tag \"{name}\" does not exist"

    async def delete_tag(self, name, owner):
        if not self.tags['tags']:
            return 'There are no tags'

        if name in self.tags['tags']:
            if self.tags['tags'][name]['owner'] == owner:
                del self.tags['tags'][name]
                self.save_tags()
                return f"The tag \"{name}\" has been deleted"
            return f"You are not the owner of the tag \"{name}\""

        return f"The tag \"{name}\" does not exist"

    async def list_tags(self):
        if not self.tags['tags']:
            return 'No tags exist'

        all_tags = ', '.join(self.tags['tags'].keys())
        '''
        if len(all_tags) > 1000:
            all_tags = list(map(''.join, zip_longest(*[iter(all_tags)] * 1000, fillvalue='')))
            return all_tags
        '''
        return all_tags

    async def edit_tag(self, name, owner, content):
        if not self.tags['tags']:
            return 'There are no tags'

        if name not in self.tags['tags']:
            return f"The tag \"{name}\" does not exist"

        if self.tags['tags'][name]['owner'] != owner:
            return f"You are not the owner of the tag \"{name}\""

        self.tags['tags'][name]['content'] = content
        return f"The tag \"{name}\" has been edited"

    async def rename_tag(self, old_name, new_name, owner):
        if not self.tags['tags']:
            return 'There are no tags'

        if old_name not in self.tags['tags']:
            return f"The tag \"{old_name}\" does not exist"

        if new_name in self.tags['tags']:
            return f"The tag \"{new_name}\" already exists"

        if self.tags['tags'][old_name]['owner'] != owner:
            return f"You are not the owner of the tag \"{old_name}\""

        self.tags['tags'][new_name] = self.tags['tags'].pop(old_name)
        self.save_tags()
        return f"The tag \"{old_name}\" has been renamed to \"{new_name}\""

    async def gift_tag(self, name, owner, new_owner):
        if not self.tags['tags']:
            return 'There are no tags'

        if name not in self.tags['tags']:
            return f"The tag \"{name}\" does not exist"

        if self.tags['tags'][name]['owner'] != owner:
            return f"You are not the owner of the tag \"{name}\""

        self.tags['tags'][name]['owner'] = new_owner
        self.save_tags()
        return f"The tag \"{name}\" has been gifted to {new_owner}"

    async def filter_tags(self, keyword):
        filtered_tags = list(filter(lambda x: keyword in x, self.tags['tags'].keys()))
        filtered_tags = ', '.join(filtered_tags)
        if not filtered_tags:
            return f"No tags contain the word {keyword}"
        return filtered_tags

    async def find_owner(self, name, fetch_user_func):
        if name in self.tags['tags']:
            try:
                user = await fetch_user_func(self.tags['tags'][name]['owner'])
                return f"The owner of \"{name}\" is {user.name}"
            except (discord.NotFound, discord.HTTPException):
                return f"Ran into an error when trying to get the owner of \"{name}\""

        return f"The tag \"{name}\" does not exist"
