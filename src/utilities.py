try:
    import googleapiclient.discovery
except ModuleNotFoundError:
    pass


class Utilities:
    def __init__(self, yt_key=None):
        self.yt_key = yt_key

    @staticmethod
    def post_help():
        return 'The commands are: tag, git, and avatar. Each one has their own help command except for git.'

    @staticmethod
    def git():
        git_url = "https://github.com/nithjino/GroupMe_Bot"
        return "Here is the source code " + git_url

    def yt_search(self, query):
        if self.yt_key is None:
            return "need a YouTube API key"
        api_service_name = "youtube"
        api_version = "v3"
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=self.yt_key)
        result = youtube.search().list(q=query, part="snippet", maxResults=1,type='video').execute()
        video_id = result['items'][0]['id']['videoId']
        return "http://youtu.be/{}".format(video_id)

