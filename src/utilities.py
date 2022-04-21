"""contains functions not big enough to put into their own module"""
import pytz
from datetime import datetime

try:
    import googleapiclient.discovery
except ModuleNotFoundError:
    pass


class Utilities:
    """contains functions not big enough to put into their own module"""

    def __init__(self, yt_key=None):
        self.yt_key = yt_key

    @staticmethod
    def post_help():
        """
        :return: a string containing what commands the bot has
        """
        return 'The commands are: tag, git, and avatar. Each one has their own help command except for git.'

    @staticmethod
    async def git():
        """
        :return: a url of the git repo of the source code
        """
        git_url = "https://github.com/nithjino/SmurfBot"
        return f"Here is the source code: {git_url}"

    @staticmethod
    def log(message):
        """
        :return: returns the current date and time
        """
        t = datetime.now(pytz.timezone('US/Eastern')).strftime("%m/%d/%Y %H:%M:%S")
        print(f"{t} - {message}")

    @staticmethod
    async def mock(message: str):
        """
        :return: message in the spongebob mocking format
        """
        message = message.lower().strip()
        result = ''
        for x in range(len(message)):
            if message[x].isspace():
                result = result + ' '
                continue

            if message[x - 1].isspace():
                if x > 0 and result[-2].isupper():
                    result = result + message[x]
                else:
                    result = result + message[x].upper()
            else:
                if x > 0 and result[-1].isupper():
                    result = result + message[x]
                else:
                    result = result + message[x].upper()

        return result
        # return ''.join([(letter.upper() if index % 2 else letter) for index, letter in enumerate(message.lower())])

    def set_yt_key(self, key):
        self.yt_key = key

    async def yt_search(self, query):
        """
        :param query: the search word(s) for youtube
        :return: youtube url of the first video in the search results
        """
        if self.yt_key is None:
            return "need a YouTube API key"
        api_service_name = "youtube"
        api_version = "v3"
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=self.yt_key)
        try:
            result = youtube.search().list(q=query, part="snippet", maxResults=1, type='video').execute()
            video_id = result['items'][0]['id']['videoId']
            return f"http://youtu.be/{video_id}"
        except Exception as e:
            print(e)
            return "Error with accessing youtube api"
