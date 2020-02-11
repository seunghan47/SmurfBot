"""Bot object each group will have that handle checking for commands and processing them"""
from threading import Timer, Event
from utilities import Utilities
from tags import Tags


class Bot:
    """Bot object each group will have that handle checking for commands and processing them"""
    def __init__(self, group, yt_key=None, delim="$"):
        """
        :param group: the group this object will read messages from
        :param yt_key: youtube api key. need it to use yt_search but not needed for other commands
        :param delim: the first character that will let the bot know it is a command. default is "$"
        """
        self.group = group
        self.delim = delim
        self.ult = Utilities(yt_key)
        self.tags = Tags(group.name, group.id, group.members)
        Timer(600, self.reload_group).start()

    def get_message(self):
        """
        :return: returns the latest message from a group. if there is an error, return None
        """
        try:
            return self.group.messages.list()[0]
        except Exception as err:
            print("bot.get_message: {}".format(err))
            return None

    def reload_tags(self):
        """
        :return: reloads the tags in the Tag object
        """
        self.tags.reload_tags()

    def reload_group(self, stop=Event()):
        """
        :param stop: threading Event. not set by default so this method would be called every 10 minutes
        :return: updates the group name, group id, and group members of a group every 10 minutes
        """
        self.group.refresh_from_server()
        print("Members of {}: {}".format(self.group.name, self.group.members))
        self.tags.update_members(self.group.members)
        self.tags.update_group_id(self.group.id)
        self.tags.update_group_name(self.group.name)
        self.tags.save_tags()

        if not stop.is_set():
            Timer(600, self.reload_group).start()

    def save_tags(self):
        """
        :return: writes the tags to a file for the group
        """
        self.tags.save_tags()

    def find_owner_name(self, user_id):
        """
        :param user_id: user_id of a member in the group
        :return: returns the nickname associated with the user_id
        """
        return list(filter(lambda x: x.user_id == user_id, self.group.members))[0]

    def find_avatar(self, message, mentions):
        """
        :param message: the avatar command. checks to see if it's a help call or actual usage
        :param mentions: list of attachments with the message. uses it to check for mentions
        :return: avatar url of person mentioned or an error message saying to mention the user
        """
        if message[2] == "help":
            return "Usage: avatar [person]"
        else:
            mentions = list(filter(lambda x: x.type == "mentions", mentions))
            if not mentions:
                user_id = mentions[0].user_ids[0]
                return self.find_owner_name(user_id).image_url
            return "Please mention the person you want the avatar of"

    def send_message(self, message):
        """
        :param message: message that will be sent to the group
        :return: message should post in the group
        """
        try:
            if isinstance(message, list):
                for res in message:
                    self.group.post(res)
            else:
                self.group.post(message)
        except Exception as err:
            print("bot.send_message: {}".format(err))

    def process_message(self, message):
        """
        :param message: checks if the message is a valid comand and execute command it is associated with
        :return: results of the command executed
        """
        if message is not None:
            try:
                message_text = message.text.lower()
                if message_text[:len(self.delim)] == self.delim:
                    user_id = message.user_id
                    owner = self.find_owner_name(user_id)
                    message_text = message_text[len(self.delim):]
                    message_text = message_text.split(" ")
                    command = message_text[0]

                    print("Processing from {}: {}".format(owner, message_text))
                    result = None
                    if command == "help":
                        result = self.ult.post_help()
                    if command == "avatar":
                        result = self.find_avatar(message_text, message.attachments)
                    if command == "git":
                        result = self.ult.git()
                    if command == "yt":
                        query = ' '.join(message_text[1:])
                        result = self.ult.yt_search(query)
                    if command == "tag":
                        result = self.tags.parse_commands(message_text, user_id, message.attachments)

                    if result is not None:
                        print("posting \"{}\" in {}".format(result, self.group.name))
                        self.send_message(result)
            except Exception as err:
                print("bot.process_message: {}".format(err))
