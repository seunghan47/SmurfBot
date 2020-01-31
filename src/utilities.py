import googleapiclient.discovery
import google-api-python-client

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

    def yt_search(self,query):
        #https://developers.google.com/youtube/v3/quickstart/python
        #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_key = self.yt_key
        api_service_name = "youtube"
        api_version = "v3"
            
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)
            
        result = youtube.search().list(q=query, part="snippet", maxResults=1,type='video').execute()['items']
        result = result[1]['snippet']
        title = result['title']
        url = "http://youtu.be/{}".format(result)
        return title + "\n" + url
