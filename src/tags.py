"""Handles all the tag related commands"""
import json
import os
from functools import reduce
from itertools import zip_longest
from atomicwrites import atomic_write


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
        self.create_json(self.group_name)
        self.tags = self.load_tags()

    @staticmethod
    def post_help():
        return 'To create a tag: "tag create [name]" while uploading a picture or by providing a link or text after ' \
               'the name. To post an already created tag: \"tag [name]\". To see what tags are made: \"tag list\".' + \
               ' To edit a tag: \"tag edit [name] [new material]\". To rename a tag:\"tag rename [current name]' + \
               ' [new name]\".'

    def create_json(self, group_name):
        tag_folder = os.path.abspath(self.bot_path + '/../tags')
        tag_json = tag_folder + "/" + group_name + '.json'

        if not os.path.exists(tag_folder):
            os.makedirs(tag_folder)
            print("created: {}".format(tag_folder))

        if not os.path.exists(tag_json):
            create_json = {'name': self.group_name, 'id': self.group_id, 'tags': {}}
            with open(tag_json, 'w') as tags:
                json.dump(create_json, tags)
            print("created: {}".format(tag_json))

    def load_tags(self):
        tag_json = os.path.abspath(self.bot_path + "/../tags/" + self.group_name + '.json')
        print("loading: {}".format(tag_json))
        with open(tag_json, 'r') as tags:
            return json.load(tags)

    def reload_tags(self):
        print("reloading tags of {}".format(self.group_name))
        self.tags = self.load_tags()

    def update_members(self, members):
        print("updating members of {}".format(self.group_name))
        self.members = members

    def save_tags(self):
        tag_json = os.path.abspath(self.bot_path + "/../tags/" + self.group_name + '.json')
        print("saving: {}".format(tag_json))
        with atomic_write(tag_json, overwrite=True) as tag_file:
            tag_file.write(json.dumps(self.tags, sort_keys=True, indent=2))

    def parse_commands(self, message, owner, mentions):
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
            new_owner = list(filter(lambda x: x.type == "mentions", mentions))[0].user_ids[0]
            tag_result = self.gift_tag(name, owner, new_owner)
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
        if name in self.tags['tags']:
            return 'The tag "{}" already exists'.format(name)
        self.tags['tags'][name] = {'owner': owner, 'content': content}
        self.save_tags()
        return 'The tag "{}" was created successfully'.format(name)

    @staticmethod
    def get_tag_content(message, mentions):
        if mentions:
            url = list(filter(lambda x: x.type == 'image' or x.type == 'video', mentions))
            return url[0].url
        return reduce((lambda x, y: x + " " + y), message)

    def post_tag(self, name):
        print("searching for tag: {}".format(name))
        if name in self.tags['tags']:
            tag = self.tags['tags'][name]['content']
            if tag.split(" ")[0] == "$tag":
                return self.post_tag(tag.split(" ")[1])
            return tag
        return 'The tag "{}" does not exist'.format(name)

    def delete_tag(self, name, owner):
        if not self.tags['tags']:
            return 'There are no tags'
        try:
            if self.tags['tags'][name]['owner'] == owner:
                del self.tags['tags'][name]
                self.save_tags()
                return 'The tag "{}" has been deleted'.format(name)
            return 'You are not the owner of the tag "{}"'.format(name)
        except KeyError:
            return 'The tag "{}" does not exist'.format(name)

    def list_tags(self):
        if not self.tags['tags']:
            return 'No tags exist'

        all_tags = ', '.join(self.tags['tags'].keys())

        if len(all_tags) > 1000:
            all_tags = list(map(''.join, zip_longest(*[iter(all_tags)] * 1000, fillvalue='')))
            return all_tags

        return all_tags

    def edit_tag(self, name, owner, content):
        if not self.tags['tags']:
            return "There are no tags to edit"
        try:
            if self.tags['tags'][name]['owner'] == owner:
                self.tags['tags'][name]['content'] = content
                self.save_tags()
                return 'The tag "{}" has been edited'.format(name)
            return 'You are not the owner of the tag "{}"'.format(name)
        except KeyError:
            return 'The tag "{}" does not exist'.format(name)

    def rename_tag(self, old_name, new_name, owner):
        if not self.tags['tags']:
            return "There are no tags"
        if new_name in self.tags['tags']:
            return 'The tag "{}" already exists. Can\'t change name to it'.format(new_name)
        try:
            if self.tags['tags'][old_name]['owner'] == owner:
                self.tags['tags'][new_name] = {'owner': owner, 'content': self.tags[old_name]['content']}
                del self.tags['tags'][old_name]
                self.save_tags()
                return 'The tag "{}" has been renamed to "{}"'.format(old_name, new_name)
            return 'You are not the owner of the tag "{}"'.format(old_name)
        except KeyError:
            return 'The tag "{}" does not exist'.format(old_name)

    def gift_tag(self, name, owner, new_owner):
        if not self.tags['tags']:
            return "There are no tags"
        try:
            if self.tags['tags'][name]['owner'] == owner:
                self.tags['tags'][name]['owner'] = new_owner
                self.save_tags()
                return 'The tag "{}" has been gifted to "{}"'.format(name, new_owner)
            return 'You are not the owner of the tag "{}"'.format(name)
        except KeyError:
            return 'The tag "{}" does not exist'.format(name)

    def filter_tags(self, keyword):
        filtered_tags = list(filter(lambda x: keyword in x, self.tags['tags'].keys()))
        filtered_tags = ', '.join(filtered_tags)
        if not filtered_tags:
            return 'No tags contain the word {}'.format(keyword)

        if len(filtered_tags) > 1000:
            tag_names = list(map(''.join, zip_longest(*[iter(filtered_tags)] * 1000, fillvalue='')))
            return tag_names

        return filtered_tags

    def find_owner(self, name):
        if name in self.tags['tags']:
            owner = self.find_owner_name(self.tags['tags'][name]['owner'])
            return "The owner of {} is {}".format(name, owner)
        return 'The tag "{}" does not exist'.format(name)

    def find_owner_name(self, user_id):
        try:
            return list(filter(lambda x: x.user_id == user_id, self.members))[0].nickname
        except IndexError:
            return "Owner not Found"
