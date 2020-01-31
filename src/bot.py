from utilities import Utilities
from tags import Tags
from threading import Timer, Event


class Bot:
    def __init__(self, group, yt_key=None, delim="$"):
        self.group = group
        print(self.group)
        self.delim = delim
        self.ult = Utilities(yt_key)
        self.tags = Tags(group.name, group.members)
        Timer(600, self.reload_members).start()

    def get_message(self):
        try:
            return self.group.messages.list()[0]
        except Exception as e:
            print("bot.get_message: {}".format(e))
            return None

    def reload_tags(self):
        self.tags.reload_tags()

    def reload_members(self, stop=Event()):
        self.group.refresh_from_server()
        print("Members of {}: {}".format(self.group.name, self.group.members))
        self.tags.update_members(self.group.members)

        if not stop.is_set():
            Timer(600, self.reload_members).start()
    
    def save_tags(self):
        self.tags.save_tags()
    
    def find_owner_name(self, user_id):
        return list(filter(lambda x: x.user_id == user_id, self.group.members))[0]

    def find_avatar(self, message, mentions):
        if message[2] == "help":
            return "Usage: avatar [person]"
        else:
            mentions = list(filter(lambda x: x.type == "mentions", mentions))
            if len(mentions) != 0:
                user_id = mentions[0].user_ids[0]
                return self.find_owner_name(user_id).image_url
            return "Please mention the person you want the avatar of"
    
    def process_message(self, message):
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

                    if command == "help":
                        result = self.ult.post_help()
                    if command == "avatar":
                        result = self.find_avatar(message_text, message.attachments)
                    if command == "git":
                        result = self.ult.git()
                    if command == "tag":
                        result = self.tags.parse_commands(message_text, user_id, message.attachments)
                    print("posting \"{}\" in {}".format(result, self.group.name))
                    if isinstance(result, list):
                        for t in result:
                            self.group.post(t)
                    else:
                        self.group.post(result)
            except Exception as e:
                print("bot.process_message: {}".format(e))
