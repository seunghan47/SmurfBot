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

'''
    def yt_search(self,message):
#from apiclient.discovery import build
#from apiclient.errors import HttpError
#from oauth2client.tools import argparser
#from groupy import attachments
        if message.lower()[:2] == "yt":
            DEVELOPER_KEY = self.yt_key
            YOUTUBE_API_SERVICE_NAME = "youtube"
            YOUTUBE_API_VERSION = "v3"
            
            query = message.lower()[3:]
            
            youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
            
            search_response = youtube.search().list(q=query
                                                    ,part="id,snippet"
                                                    ,maxResults=1
                                                    ,type='video').execute()
            video = []
            for search_result in search_response.get("items", []):
                video_description= search_result['snippet']['title'] + " from " + search_result['snippet']['channelTitle']
                video.append('http://youtu.be/' + search_result['id']['videoId'])
                
            self.active_group.post(video_description)
            self.active_group.post(video[0])
'''
