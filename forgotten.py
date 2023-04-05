import googleapiclient.discovery
import country_codes

class ForgottenYoutube():
    def __init__(self):
        self.api_key = None
        self.youtube = None
        self.playlist_id = None

        self.unavailable_videos = False
        self.restricted_videos = False

        #Contains a list of filters set by the user
        self.filters = list()

        self.output_file = None

        #Contains list of all deleted or private videos from a playlist
        self.unavailable_videos_id = list()
        #Contains a list of blocked videos in region(s) from a playlist
        self.videos_id = list()

        #Used for stats
        self.total_video = 0
        self.count_private_videos = 0
        self.count_deleted_videos = 0
        self.count_age_restricted_videos = 0
        self.count_region_restricted_videos = 0
        self.count_region_restricted_filters_videos = 0
        

    def set_api_key(self, api_key):
        self.api_key = api_key

    def setup_youtube_api_client(self):
        self.youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = self.api_key)

    #Check if use gave URL or ID
    def set_playlist_id(self, playlist_id):
        #I don't use regex, split in case a URL is given
        try:
            self.playlist_id = playlist_id.split("?list=")[1]
        except IndexError:
            self.playlist_id = playlist_id

    def set_unavailable_videos(self):
        self.unavailable_videos = True

    def set_restricted_videos(self):
        self.restricted_videos = True

    def set_output_file(self, output_file):
        self.output_file = output_file

    #Returns the playlist given an id
    def get_playlist(self):
        try:
            response = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                maxResults=50,
                playlistId=self.playlist_id
            ).execute()

            return response
        except:
            print("Error while retrieving the playlist... Is it public? Existing?")
            exit()

    #Browse a playlist and retrieve unavailable and blocked videos
    def browse_full_playlist(self):
        response = self.get_playlist()
        self.select_videos(response)

        nextPageToken = response.get('nextPageToken')

        #If there is a nextPageToken field then continue until there are no more videos
        while('nextPageToken' in response):
            try:
                response = self.youtube.playlistItems().list(
                    pageToken=nextPageToken,
                    part="snippet,contentDetails",
                    maxResults=50,
                    playlistId=self.playlist_id
                ).execute()
            except:
                print("Error while retrieving the playlist... Is it public? Existing?")
                exit()

            self.select_videos(response)

            nextPageToken = response.get('nextPageToken')


    #Get the deleted, private or blocked videos
    def select_videos(self, response):
        try:
            for video in response['items']:
                self.total_video += 1
                if(self.unavailable_videos):
                    if(video['snippet']['title'] == 'Deleted video'):
                        self.count_deleted_videos += 1
                        self.unavailable_videos_id.append(video['snippet']['resourceId']['videoId'])
                    elif(video['snippet']['title'] == 'Private video'):
                    
                        self.count_deleted_videos += 1
                        self.unavailable_videos_id.append(video['snippet']['resourceId']['videoId'])
                if(self.restricted_videos):
                    if(video.get('contentDetails')):
                        self.videos_id.append(video['snippet']['resourceId']['videoId'])
        except:
            print("Not possible to retrieve data from playlist... Is it public? Existing?")
            exit()

    def convert_codes_to_countries(self, codes):
        countries = list()

        for code in codes:
            countries.append(country_codes.abbrev_to_country[code])

        return ', '.join(countries)

    #Returns only videos that are restricted in specific country (can have multiple filters)
    def set_region_filter(self, filters):
        self.filters = filters.replace(" ","").split(",")

    def save_to_file(self, content):
        with open(self.output_file, 'a') as file:
            file.write(content)


    def print_unavailable_videos(self):
        if(self.unavailable_videos):

            content = f"List of deleted or private videos:\n\n"


            if(len(self.unavailable_videos_id) == 0):
                content += f"None of the videos are deleted or private\n"
                if(self.output_file != None):
                    self.save_to_file(content)
                else:
                    print(content)
                return

            for video_id in self.unavailable_videos_id:
                content += f"https://web.archive.org/web/*/https://www.youtube.com/watch?v={video_id}\n"
                content += f"https://www.google.com/search?q=https://www.youtube.com/watch?v={video_id}\n"
                content += f"https://webcache.googleusercontent.com/search?q=cache:https://www.youtube.com/watch?v={video_id}\n\n"
                
            if(self.output_file != None):
                self.save_to_file(content)
            else:
                print(content)


    def print_region_restricted_videos(self):
        if(self.restricted_videos):

            content = f"List of blocked videos in specific regions:\n"

            if(len(self.filters) != 0):
                content += f"Filters applied on the following regions: {self.convert_codes_to_countries(self.filters)}\n"

            if(self.output_file != None):
                self.save_to_file(content)
            else:
                print(content)
            #Reset
            content = ""

            for video_id in self.videos_id:
                response = self.youtube.videos().list(
                    part="snippet,contentDetails",
                    id=video_id
                ).execute()


                for video in response['items']:
                    try:
                        if('blocked' in video['contentDetails']['regionRestriction']):
                            self.count_region_restricted_videos += 1
                            title = video['snippet']['title']

                            content = f"{video['snippet']['title']} (https://www.youtube.com/watch?v={video['id']})"

                            #Check the number of restricted regions. If number = 249 then blocked in all regions
                            if(len(video['contentDetails']['regionRestriction']['blocked']) == 249):
                                self.count_region_restricted_filters_videos += 1
                                content += f" is blocked in every country\n"
                                content += f"https://web.archive.org/web/*/https://www.youtube.com/watch?v={video['id']}\n"
                            else:

                                if(len(self.filters) == 0):
                                    content += f" is blocked in the following regions: {self.convert_codes_to_countries(video['contentDetails']['regionRestriction']['blocked'])}\n"
                                    content += f"https://web.archive.org/web/*/https://www.youtube.com/watch?v={video['id']}\n"
                                else:
                                    if(any(region in self.filters for region in video['contentDetails']['regionRestriction']['blocked'])):
                                        self.count_region_restricted_filters_videos += 1
                                        content = f"{video['snippet']['title']} (https://www.youtube.com/watch?v={video['id']})"
                                        content += f" is blocked in the following regions: {self.convert_codes_to_countries(video['contentDetails']['regionRestriction']['blocked'])}\n"
                                        content += f"https://web.archive.org/web/*/https://www.youtube.com/watch?v={video['id']}\n"
                                    else:
                                        continue

                            if(self.output_file != None):
                                self.save_to_file(content)
                            else:
                                print(content)
                            content = ""

                    except KeyError:
                        pass

            if(len(self.filters) == 0):
                if(self.count_region_restricted_videos == 0):
                    content = f"None of the videos are blocked\n\n"
            else:
                if(self.count_region_restricted_filters_videos == 0):
                    content = f"None of the videos are blocked\n\n"

            if(self.output_file != None):
                self.save_to_file(content)
            else:
                print(content)

    def print_age_restricted_videos(self):
        if(self.restricted_videos):

            content = f"List of age restricted videos:\n"

            if(self.output_file != None):
                self.save_to_file(content)
            else:
                print(content)
            #Reset
            content = ""

            for video_id in self.videos_id:
                response = self.youtube.videos().list(
                    part="snippet,contentDetails",
                    id=video_id
                ).execute()


                for video in response['items']:
                    try:
                        if('ytAgeRestricted' in video['contentDetails']['contentRating']['ytRating']):

                            self.count_age_restricted_videos += 1
                            title = video['snippet']['title']

                            content = f"{video['snippet']['title']} (https://www.youtube.com/watch?v={video['id']})"

                            if(self.output_file != None):
                                self.save_to_file(content)
                            else:
                                print(content)
                            content = ""

                    except KeyError:
                        pass

            if(self.count_age_restricted_videos == 0):
                content = f"None of the videos are age restricted\n\n"

            if(self.output_file != None):
                self.save_to_file(content)
            else:
                print(content)



    #Print all stats
    def print_stats(self):

        content = f"Global stats:\n\n"
        content += f"Total number videos: {self.total_video}\n"

        if(self.unavailable_videos):
            content += f"Number of private videos: {self.count_private_videos}\n"
            content += f"Number of deleted videos: {self.count_deleted_videos}\n"

        if(self.restricted_videos):
            content += f"Number of age restricted videos: {self.count_age_restricted_videos}\n"

            if(len(self.filters) == 0):
                content += f"Number of videos blocked in at least one region: {self.count_region_restricted_videos}\n"
            else:
                content += f"Number of videos blocked in the filtered regions ({self.convert_codes_to_countries(self.filters)}): {self.count_region_restricted_filters_videos}\n"

        if(self.output_file != None):
            self.save_to_file(content)
        else:
            print(content)


    def run(self):
        self.setup_youtube_api_client()
        self.browse_full_playlist()
        self.print_unavailable_videos()
        self.print_region_restricted_videos()
        self.print_age_restricted_videos()
        self.print_stats()