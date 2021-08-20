"""Handles all the tag related commands"""
import json
import os
from functools import reduce
from itertools import zip_longest
from atomicwrites import atomic_write
from utilities import Utilities


class Tags:
    """Handles all the tag related commands"""
    def __init__(self, group_name, group_id, members):
        """
        :param group_name: name of the group
        :param group_id: id of the group
        :param members: list of members of the group
        """
        self.group_name = group_name
        self.group_id = group_id
        self.members = members
        self.bot_path = os.path.dirname(os.path.realpath(__file__))
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

    def create_json(self, group_id):
        """
        :param group_id: id of the group
        :return: creates the tags directory if it doesn't exist. creates the tags json file for the group
        if it doesn't exist
        """
        tag_folder = os.path.abspath(self.bot_path + '/../tags')
        tag_json = tag_folder + "/" + group_id + '.json'

        if not os.path.exists(tag_folder):
            os.makedirs(tag_folder)
            Utilities.log(f"{self.group_name}: created: {tag_folder}")

        if not os.path.exists(tag_json):
            create_json = {'name': self.group_name, 'id': self.group_id, 'tags': {}}
            with open(tag_json, 'w') as tags:
                json.dump(create_json, tags)
            Utilities.log(f"{self.group_name}: created: {tag_json}")

    def load_tags(self):
        """
        :return: dictionary of the group's tag json file
        """
        self.create_json(self.group_id)
        tag_json = os.path.abspath(self.bot_path + "/../tags/" + self.group_id + '.json')
        Utilities.log(f"{self.group_name}: loading: {tag_json}")
        with open(tag_json, 'r') as tags:
            return json.load(tags)

    def save_tags(self):
        """
        :return: dumps the group's tag to the disk
        """
        tag_json = os.path.abspath(self.bot_path + "/../tags/" + self.group_id + '.json')
        Utilities.log(f"{self.group_name}: saving: {tag_json}")
        with atomic_write(tag_json, overwrite=True) as tag_file:
            tag_file.write(json.dumps(self.tags, sort_keys=True, indent=2))

    def reload_tags(self):
        """
        :return: updates the tags using the group's json file on disk
        """
        Utilities.log(f"{self.group_name}: reloading tags of {self.group_name}")
        self.tags = self.load_tags()

    def update_members(self, members):
        """
        :param members: list of members from a group
        :return: updates self.members
        """
        self.members = members

    def update_group_id(self, group_id):
        """
        :param group_id: id of group
        :return: updates group id in tags json
        """
        if group_id != self.group_id:
            self.group_id = group_id
            self.tags['id'] = self.group_id

    def update_group_name(self, group_name):
        """
        :param group_name: name of group
        :return: updates group name in tags json
        """
        if group_name != self.group_name:
            self.group_name = group_name
            self.tags['name'] = self.group_name

    def parse_commands(self, message, owner, mentions):
        """
        :param message: contains the command and argument(s) for that command
        :param owner:  user id of whoever sent the command
        :param mentions: list of images/videos upload to groupme or mentions
        :return: result of the command that was invoked
        """
        command = message[1].rstrip()
        if command == "create":
            name = message[2].rstrip()
            content = self.get_tag_content(message[3:], mentions)
            tag_result = self.create_tag(name, content, owner)
        elif command == "delete":
            tag_result = self.delete_tag(message[2].rstrip(), owner)
        elif command == "list":
            tag_result = self.list_tags()
        elif command == "help":
            tag_result = self.post_help()
        elif command == "edit":
            name = message[2].rstrip()
            content = self.get_tag_content(message[3:], mentions)
            tag_result = self.edit_tag(name, owner, content)
        elif command == "rename":
            old_name = message[2].rstrip()
            new_name = message[3].rstrip()
            tag_result = self.rename_tag(old_name, new_name, owner)
        elif command == "gift":
            name = message[2].rstrip()
            try:
                new_owner = list(filter(lambda x: x.type == "mentions", mentions))[0].user_ids[0]
                tag_result = self.gift_tag(name, owner, new_owner)
            except IndexError:
                tag_result = "Please mention who should be the new owner"
        elif command == "owner":
            if len(message) == 2:
                tag_result = self.post_tag(message[1].rstrip())
            else:
                tag_result = self.find_owner(message[2].rstrip())
        elif command == "filter":
            if len(message) == 2:
                tag_result = self.post_tag(message[1].rstrip())
            else:
                tag_result = self.filter_tags(message[2].rstrip())
        else:
            tag_result = self.post_tag(message[1].rstrip())

        return tag_result

    def create_tag(self, name, content, owner):
        """
        :param name: name of the tag
        :param content: body of the tag.
        :param owner: user id of whoever invoked this specific command
        :return: confirmation that the tag was created or if it already exists
        """
        if name in self.tags['tags']:
            return f"The tag \"{name}\" already exists"
        self.tags['tags'][name] = {'owner': owner, 'content': content}
        self.save_tags()
        return f"The tag \"{name}\" was created successfully"

    @staticmethod
    def get_tag_content(message, mentions):
        """
        :param message: a list of the potential content of a tag
        :param mentions: a list of potential content of a groupme uploaded image or video of a tag
        :return: a single string made from message or the image/video url from mentions
        """
        if mentions:
            url = list(filter(lambda x: x.type == 'image' or x.type == 'video', mentions))
            return url[0].url
        return reduce((lambda x, y: x + " " + y), message)

    def post_tag(self, name):
        """
        :param name: key of the tag content
        :return: content of the tag or a message saying the tag doesn't exist
        """
        Utilities.log(f"{self.group_name}: searching for tag: {name} to post")
        if name in self.tags['tags']:
            content = self.tags['tags'][name]['content']
            if content.split(" ")[0] == "$tag":
                return self.post_tag(content.split(" ")[1])
            return content
        return f"The tag \"{name}\" does not exist"

    def delete_tag(self, name, owner):
        """
        :param name: key of the tag content
        :param owner: user id of who invoked this command
        :return: deletes key if owner passed to this method matches the owner of the tag. otherwise, returns
        an error message
        """
        Utilities.log(f"{self.group_name}: searching for tag: {name} to delete")
        if not self.tags['tags']:
            return 'There are no tags'
        try:
            if self.tags['tags'][name]['owner'] == owner:
                del self.tags['tags'][name]
                self.save_tags()
                return f"The tag \"{name}\" has been deleted"
            return f"You are not the owner of the tag \"{name}\""
        except KeyError:
            return f"The tag \"{name}\" does not exist"

    def list_tags(self):
        """
        :return: either a string or list of all the tag keys
        """
        if not self.tags['tags']:
            return 'No tags exist'

        all_tags = ', '.join(self.tags['tags'].keys())

        if len(all_tags) > 1000:
            all_tags = list(map(''.join, zip_longest(*[iter(all_tags)] * 1000, fillvalue='')))
            return all_tags

        return all_tags

    def edit_tag(self, name, owner, content):
        """
        :param name: key of the tag content
        :param owner: user id of whoever invoked this command
        :param content: new content for that tag
        :return: updates the content of the tag or returns a message saying you can't
        """
        if not self.tags['tags']:
            return "There are no tags to edit"
        try:
            if self.tags['tags'][name]['owner'] == owner:
                self.tags['tags'][name]['content'] = content
                self.save_tags()
                return f"The tag \"{name}\" has been edited"
            return f"You are not the owner of the tag \"{name}\""
        except KeyError:
            return f"The tag \"{name}\" does not exist"

    def rename_tag(self, old_name, new_name, owner):
        """
        :param old_name: current key name of the tag
        :param new_name: new key name of the etag
        :param owner: user id of whoever invoked this command
        :return: updates the tag's name or returns a message saying you can't
        """
        Utilities.log(f"{self.group_name}: Renaming tag \"{old_name}\" to \"{new_name}\"")
        if not self.tags['tags']:
            return "There are no tags"
        if new_name in self.tags['tags']:
            return f"The tag \"{new_name}\" already exists. Can't change {old_name} to it"
        try:
            if self.tags['tags'][old_name]['owner'] == owner:
                self.tags['tags'][new_name] = self.tags['tags'].pop(old_name)
                self.save_tags()
                return f"The tag \"{old_name}\" has been renamed to \"{new_name}\""
            return f"You are not the owner of the tag \"{old_name}\""
        except KeyError:
            return f"The tag \"{old_name}\" does not exist"

    def gift_tag(self, name, owner, new_owner):
        """
        :param name: key of the tag content
        :param owner: user id of whoever invoked this command
        :param new_owner: user id of new owner of the tag
        :return: updates owner or returns a message saying you can't
        """
        Utilities.log(f"Attempting to gift the tag \"{name}\" from {owner} to {new_owner}")
        if not self.tags['tags']:
            return "There are no tags"
        try:
            if self.tags['tags'][name]['owner'] == owner:
                self.tags['tags'][name]['owner'] = new_owner
                self.save_tags()
                new_owner = self.find_owner_name(new_owner)
                return f"The tag \"{name}\" has been gifted to {new_owner}"
            return f"You are not the owner of the tag \"{name}\""
        except KeyError:
            return f"The tag \"{name}\" does not exist"

    def filter_tags(self, keyword):
        """
        :param keyword: word a tag name should contain
        :return: list of tags that contain keyword or a message saying none exists
        """
        filtered_tags = list(filter(lambda x: keyword in x, self.tags['tags'].keys()))
        filtered_tags = ', '.join(filtered_tags)
        if not filtered_tags:
            return "No tags contain the word {keyword}"

        # there is a character limit for a groupme message
        if len(filtered_tags) > 1000:
            tag_names = list(map(''.join, zip_longest(*[iter(filtered_tags)] * 1000, fillvalue='')))
            return tag_names

        return filtered_tags

    def find_owner(self, name):
        """
        :param name: tag name
        :return: nickname of the owner of the tag
        """
        Utilities.log(f"Attempting to find the owner of the tag \"{name}\"")
        if name in self.tags['tags']:
            owner = self.find_owner_name(self.tags['tags'][name]['owner'])
            return f"The owner of \"{name}\" is {owner}"
        return f"The tag \"{name}\" does not exist"

    def find_owner_name(self, user_id):
        """
        :param user_id: integer representing the user id of a potential group member
        :return:
        """
        Utilities.log(f"Attempting to find the name of the user_id \"{user_id}\"")
        try:
            return list(filter(lambda x: x.user_id == user_id, self.members))[0].nickname
        except IndexError:
            return "Owner not Found"
