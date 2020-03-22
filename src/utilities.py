"""contains functions not big enough to put into their own module"""
try:
    import googleapiclient.discovery
except ModuleNotFoundError:
    pass
import requests

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
    def git():
        """
        :return: a url of the git repo of the source code
        """
        git_url = "https://github.com/nithjino/GroupMe_Bot"
        return "Here is the source code " + git_url

    def yt_search(self, query):
        """
        :param query: the search word(s) for youtube
        :return: youtube url of the first video in the search results
        """
        if self.yt_key is None:
            return "need a YouTube API key"
        api_service_name = "youtube"
        api_version = "v3"
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=self.yt_key)
        result = youtube.search().list(q=query, part="snippet", maxResults=1, type='video').execute()
        video_id = result['items'][0]['id']['videoId']
        return "http://youtu.be/{}".format(video_id)

    def is_neg(self, num):
        if num > 0:
            return "+{}".format(num)
        return num

    def corona(self, query=""):
        url = "https://corona-stats.online/us?format=json"
        data = requests.get(url=url).json()
        states = {
                    'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa', 'AZ': 'Arizona',
                    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia',
                    'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa',
                    'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky',
                    'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan',
                    'MN': 'Minnesota', 'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi',
                    'MT': 'Montana', 'NA': 'National', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska',
                    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York',
                    'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico',
                    'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee',
                    'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VI': 'Virgin Islands', 'VT': 'Vermont',
                    'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming',
                    'FM': 'Federated States of Micronesia', 'MH': 'Marshall Islands', 'PW': 'Palau'
                 }

        if len(query) == 0:
            formatted = ""
            for i in range(0, 5):
                state = data[i]
                st = state['province']
                c = state['confirmed']
                r = state['recovered']
                d = state['deaths']
                # a = state['active']
                dr = state['mortalityPer']
                confirmed_change = self.is_neg(int(state['confirmedByDay'][-1]) - int(state['confirmedByDay'][-2]))
                recovered_change = self.is_neg(int(state['recoveredByDay'][-1]) - int(state['recoveredByDay'][-2]))
                deaths_change = self.is_neg(int(state['deathsByDay'][-1]) - int(state['deathsByDay'][-2]))

                formatted = formatted + "{}: {} confirmed ({}) /{} recovered ({}) /{} dead ({}) ({}%)\n".format(st, c,
                                                        confirmed_change, r, recovered_change, d, deaths_change, dr)
            return formatted
        try:
            if len(query) == 2:
                query = states[query.upper()]

            state = list(filter(lambda x: x['province'].lower() == query.lower(), data))[0]
            st = state['province']
            c = state['confirmed']
            r = state['recovered']
            d = state['deaths']
            #a = state['active']
            dr = state['mortalityPer']
            confirmed_change = self.is_neg(int(state['confirmedByDay'][-1]) - int(state['confirmedByDay'][-2]))
            recovered_change = self.is_neg(int(state['recoveredByDay'][-1]) - int(state['recoveredByDay'][-2]))
            deaths_change = self.is_neg(int(state['deathsByDay'][-1]) - int(state['deathsByDay'][-2]))

            return "{}: {} confirmed ({}) /{} recovered ({}) /{} dead ({}) ({}%)\n".format(st, c, confirmed_change, r,
                                                                            recovered_change, d, deaths_change, dr)
        except IndexError:
            return "state or territory not found"

