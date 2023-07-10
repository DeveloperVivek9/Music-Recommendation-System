import numpy as np
import pandas as pd
import vaex
import vaex.ml
from IPython.display import display

class Recommender(object):
    """
    Recommends songs based on locally stored spotify features 
    """
    def __init__(self,DATABASE_PATH):
        self.df=vaex.open(DATABASE_PATH)  
        self.genre_mapping={"Pop":'pop',"Country":'country',"Reggae":'reggae',"Jazz":'jazz',
                       "Blues":'blues',"Disco":'disco',
                        "Classical":'classical',"Folk":'folk',
                            "Hip-Hop":'hip hop',"Metal":'metal',"Rock":'rock',
                            "Electronic":'electro',
                            "pop":'pop',"country":'country',
                            "reggae":'reggae',"jazz":'jazz',
                       "blues":'blues',"disco":'disco',
                            "classical":'classical',"folk":'folk',
                       "hip hop":'hip hop',"metal":'metal',
                            "rock":'rock',"electro":'electro'}
        
    def Euclidean_distance(self,input_features,required_features,column_list,*features):
        both = set(required_features).intersection(column_list)
        indices= sorted([column_list.index(x) for x in both])
        #We will be selecting features here based on required features therefore indices off of features_list must correspond to given parameters
        res_list = map(features.__getitem__, indices)
        summ=0
        for index,f in enumerate(res_list):
            summ+=(f-input_features[index])**2
        return np.sqrt(summ)

    def check_id(self,track_id,df):
        if(df==None):
            df=self.df 
        if(len(df[df["Spotify_Track_ID"]==track_id])>0):
            print("Track ID present in database ->",end= " ")
            return True
        else:
            print("Track ID not present in database ->",end=" ")
            return False
        
    def get_features(self,track_id,required_features):
        df=self.df
        features=df[df["Spotify_Track_ID"]==track_id][required_features].to_dict()
        #If at all track id duplicates exists, takes the first one's features. [0] takes the first element
        features=dict([(k,v[0].as_py()) for k,v in features.items()])
        return features
    
        
    def recommend(self,features,genre,spotify,track_id,no_of_recommendations=10,measure="euclidean"):
        """
        Recommends songs along with their spotify track id 
        """
        required_features=list(features.keys())
        df=self.df
        column_list=list(df.columns)  
        null_features=[feature for feature,value in features.items() if value == None]
        if(len(null_features)>0):
            print("Since features not complete, average features will be found ->",end=" ")
            both = set(null_features).intersection(column_list)
            indices= sorted([column_list.index(x) for x in both])
            for i in indices:
                print(column_list[i],end=" ")
                features[column_list[i]]=df[:,i].mean().item()
            print("-> Average features found :",end=" ")
        display(features)

        if(genre in self.genre_mapping.keys()):
            print("Database filtered ->",end=" ")
            df=df[df['Genre']==self.genre_mapping[genre]]
        else:
            print("Genre not in our database ->",end=" ")
        
        track_id_not_in_filtered_database=False
        if(track_id):
            if(self.check_id(track_id,df)):
                #This means that features will not be at the end of our dataframe which is the assumption the logic makes.
                track_id_not_in_filtered_database=True
            else:
                #Since despite track_id existing in our database, it's not in our filtered database.
                #This can mean there is a mismatch between the predicted class and the label in our database.
                pandas_df= pd.DataFrame([features], columns=required_features)
                pandas_df=vaex.from_pandas(df=pandas_df)
                df = vaex.concat([df,pandas_df])
        else:     
            pandas_df= pd.DataFrame([features], columns=required_features)
            pandas_df=vaex.from_pandas(df=pandas_df)
            df = vaex.concat([df,pandas_df])
            
        scaler = vaex.ml.StandardScaler(features=list(df.columns)[1:-2], prefix='scaled_')
        scaler.fit(df)
        df = scaler.transform(df)
        #In vaex, when taking column list, virtual columns don't show up REMEMBER
        #parameters given in the function must be in the same order as in list(df.columns) i.e. scaled_Energy after scaled_duration just like in list, Energy after Duration
        scaled_req=["scaled_"+x for x in required_features]
        if(track_id_not_in_filtered_database!=True):
            scaled_features=df[scaled_req][-1]
        else:
            scaled_features=df[df["Spotify_Track_ID"]==track_id][scaled_req].values.tolist()[0]
        print("Features scaled ->",end=" ")
        
        if(measure.lower()=='euclidean'):
            df["distance"]=self.Euclidean_distance(scaled_features,required_features,column_list,df.Spotify_Track_ID, df.scaled_Acousticness, df.scaled_Danceability, 
                                df.scaled_Duration_Ms, df.scaled_Energy, df.scaled_Instrumentalness, df.scaled_Key, 
                                df.scaled_Liveness, df.scaled_Loudness, df.scaled_Mode, 
                                df.scaled_Speechiness, df.scaled_Tempo, df.scaled_Time_Signature,df.scaled_Valence,df.Genre_List,df.Genre)
        print("Distance found ->",end=" ")  
        df=df.sort('distance', ascending=True)
        
        recommended_track_ids=df[1:no_of_recommendations+1].Spotify_Track_ID.tolist()
        print(f"Distance sorted and similar track ids found :")
        display(recommended_track_ids)
        
        recommendation_list=list()
        added_tracks=list()
        for track_id in recommended_track_ids:
            artist_title_dict=spotify.recognize_trackID(track_id)
            s=(artist_title_dict["Artists"]+artist_title_dict["Title"]).lower()
            if(s not in added_tracks):
                artist_title_dict['Spotify_URI']="https://open.spotify.com/track/"+track_id
                recommendation_list.append(artist_title_dict)
                added_tracks.append(s)
            if(len(recommendation_list)==no_of_recommendations):
                break
        print("Recommendations compiled")
        display(recommendation_list)
        return recommendation_list