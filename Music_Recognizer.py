from glob import glob
import os
from ShazamAPI import Shazam

class Music_Recognizer(object):
    """
    Returns Artists and name of the song from various file formats
    Right now only mp3/wav supported
    """
    def recognize_song_from_mp3(self,mp3_file,search="best"):
        """
        Takes in two inputs. mp3_file -> A string and search_full -> a boolean value.
        Returns a list of dictionaries where key -> Artist name, value -> Title of song.

        mp3_file -> Name of the file
        [including directory in case it's not located in the same directory as the code.]
        Example : "D:/Problem Music/Heheh.mp3"
        """
        try:
            mp3_file_content_to_recognize = open(mp3_file, 'rb').read()
            shazam = Shazam(mp3_file_content_to_recognize)
            recognize_generator = shazam.recognizeSong()
        except:
            print("We couldn't recognize the song")
            return ("","")
        Recognized_Song_List=list()
        flag=True
        count=1
        while flag:
            print(count,end=" ")
            count+=1
            try:
                L=next(recognize_generator)
                artist=L[1]['track']['subtitle']
                title=L[1]['track']['title']
                if(search=="best" and {artist:title} in Recognized_Song_List):
                    print(f"\nWe recognized the song to be : {artist} - {title}")
                    return (artist,title)
                if(search=='first'):
                    print(f"\nWe recognized the song to be : {artist} - {title}")
                    return (artist,title)
                Recognized_Song_List.append({L[1]['track']['subtitle']:L[1]['track']['title']})
            except StopIteration:
                print("\nSearched till the end of the track.")
                break
            except Exception as e:
                continue
        if(len(Recognized_Song_List)>0):
            max_value=0
            max_index=0
            for index,value in enumerate(Recognized_Song_List):
                if(max_value<Recognized_Song_List.count(value)):        
                    max_value=Recognized_Song_List.count(value)
                    max_index=index
            artist=next(iter(Recognized_Song_List[max_index].keys()))
            title=next(iter(Recognized_Song_List[max_index].values()))
            print(f"We recognized the song to be : {artist} - {title}")
            return (artist,title)
        else:
            print("We couldn't recognize the song")
            return ("","")