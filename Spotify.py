import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import Levenshtein as lev
from IPython.display import display

class Spotify(object):
    """
    Two functions : search_song_spotify, recognize_song_from_trackID
    """
    def __init__(self,SECRETS_PATH):
        #Getting API CLIENT ID AND SECRET and setting up API
        secret_dict=dict()
        with open(SECRETS_PATH) as f:
            for line in f:
                (key, val) = line.split()
                secret_dict[key] = val
        CLIENT_ID=secret_dict['SPOTIFY_CLIENT_ID']
        CLIENT_SECRET=secret_dict['SPOTIFY_CLIENT_SECRET']
        CLIENT_CREDENTIALS_MANAGER = SpotifyClientCredentials(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET
        )
        self.client = spotipy.Spotify(client_credentials_manager=CLIENT_CREDENTIALS_MANAGER)
        
    def min_leven_distance(self,word,words): 
        w1=word.lower()
        min_dist=lev.distance(w1,words[0].lower())
        min_index=0
        for index,i in enumerate(words):
            d=lev.distance(w1,i.lower())
            if(d<min_dist):
                min_index=index
                min_dist=d
            elif(d==min_dist and w1 in i.lower() and len(i)<len(words[min_index])):
                min_index=index
                min_dist=d
        return words[min_index]
    
    def get_genre_list(self,track_id):
        genre_list=list()
        d=self.client.track(track_id)
        for artist in d['artists']:
            a=self.client.artist(artist['id'])
            genre_list.extend(a['genres'])
        return genre_list
        
    def get_track_id(self,artist,title):
        #If artist or song isn't recognized, return features as None.
        if(artist=="" or title==""):
            return None
        artist=artist.title()
        title=title.title()
        artist_query="%20".join(artist.split())
        title_query="%20".join(title.split())
        search_results=self.client.search("%20track:"+title_query+"%20artist:"+artist_query)
        query_dict=dict() 
        for index,result in enumerate(search_results['tracks']['items']):
            if(result['type']=='track'):
                query_dict[index]=result['artists'][0]['name']+" "+result['name']
                
        #If no search results, return none as features.
        if(len(query_dict)<1):
            print("Didn't get any search results. Returning track ID as None")
            return None
        
        #Finding most similar search result from gven artist title using Levenshtein distance.
        word=artist+" "+title
        print("Searching for :",word)
        words=list(query_dict.values())
        print("Search queries :",words)
        most_similar_query=self.min_leven_distance(word,words)
        most_similar_query=[index for index, song in query_dict.items() if song == most_similar_query][0]
        result=search_results['tracks']['items'][most_similar_query]
        print(f"Found {result['artists'][0]['name']} - {result['name']} to be the most similar to the given query")
        track_id=result['uri'].split(":")[2]
        print('Track ID of song :',track_id)
        return track_id
        
    def get_features(self,track_id,required_features=['Danceability','Energy','Liveness','Tempo','Valence']):  
        audio_features=self.client.audio_features(track_id)[0]
        #Converting required features and retrieved featured from spotify into lowercase to avoid misses
        audio_features=dict((k.lower(), v) for k,v in audio_features.items())
        required_features_2=[x.lower() for x in required_features]
        
        features={key: audio_features[key] for key in audio_features.keys() & required_features_2}
        features=dict((k.title(), v) for k,v in features.items())

        #features=list(dict(sorted(features.items())).values())
        #If required features not retrieved, return None.
        if(len(features)<len(required_features)):
            print(f"Returning incomplete features : {features}")  
            #print(f"Features retrieved less than required features : {features}. For simplicity, returning None.")
            #return dict((k,None) for k in required_features)
        else:
            print(f"Successfully retrieved features : {features}")
        return features
    
    def recognize_trackID(self,track_id):
        #Track_ID=i['Spotify_URI'].split("/")[-1]
        Track_details=self.client.track(track_id)
        artists=",".join([x['name'] for x in Track_details['artists']])
        title=Track_details['name']
        preview_url=Track_details['preview_url']
        return {'Artists':artists,'Title':title,'Preview_URL':preview_url}