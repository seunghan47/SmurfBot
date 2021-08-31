"""Handles all the tag related commands"""
import json
import os
from functools import reduce
from itertools import zip_longest
from atomicwrites import atomic_write
from utilities import Utilities


class Tags:
    """Handles all the tag related commands"""
    def __init__(self, guild, tags_json_path):
        """
        :param group_name: name of the group
        :param group_id: id of the group
        :param members: list of members of the group
        """
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
        tag_json = os.path.abspath(self.bot_path + "/../tags/" + self.group_id + '.json')
        Utilities.log(f"{self.group_name}: saving: {tag_json}")
        with atomic_write(tag_json, overwrite=True) as tag_file:
            tag_file.write(json.dumps(self.tags, sort_keys=True, indent=2))

    def parse_commands(self, **kwargs):
        print(f"tags parse_commands kwargs: {kwargs}")
        message = kwargs['args']
        command = message[0].rstrip()
        if command == "create":
            pass
        elif command == "delete":
            pass
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
            pass
        elif command == "filter":
            pass
        else:
            tag_result = self.post_tag(command.strip())

        return tag_result

    def create_tag(self, name, content, owner):
        pass

    def get_tag_content(message, mentions):
        pass

    def post_tag(self, name):
        if name in self.tags['tags']:
            return self.tags['tags'][name]['content']
        return f"The tag \"{name}\" does not exist"

    def delete_tag(self, name, owner):
        pass

    def list_tags(self):
        if not self.tags['tags']:
            return 'No tags exist'

        all_tags = ', '.join(self.tags['tags'].keys())
        '''
        if len(all_tags) > 1000:
            all_tags = list(map(''.join, zip_longest(*[iter(all_tags)] * 1000, fillvalue='')))
            return all_tags
        '''
        return all_tags

    def edit_tag(self, name, owner, content):
        pass

    def rename_tag(self, old_name, new_name, owner):
        pass

    def gift_tag(self, name, owner, new_owner):
        pass

    def filter_tags(self, keyword):
        pass

    def find_owner(self, name):
        pass

    def find_owner_name(self, user_id):
       pass
