import librosa
import math
import numpy as np

class CNN():
    """
    Predicts Genre of a song file using CNN
    """
    def __init__(self,genre_list=None,SAMPLE_RATE=None,TRACK_DURATION=None,num_mfcc=None,n_fft=None,hop_length=None,
        num_segments=None):
        self.genre_list = genre_list if genre_list is not None else ['Blues','Classical','Country','Disco','Hip-Hop','Jazz','Metal','Pop','Reggae','Rock']    
        self.SAMPLE_RATE = SAMPLE_RATE if SAMPLE_RATE is not None else 22050
        self.TRACK_DURATION = TRACK_DURATION if TRACK_DURATION is not None else 30        
        self.num_mfcc = num_mfcc if num_mfcc is not None else 13        
        self.n_fft = n_fft if n_fft is not None else 2048        
        self.hop_length = hop_length if hop_length is not None else 512         
        self.num_segments = num_segments if num_segments is not None else 10    
                
    def extract_features(self,file_path):
        """
        Gets mel spectrograms for the audio file using the paramaters given during object initialization
        """
        SAMPLES_PER_TRACK = self.SAMPLE_RATE * self.TRACK_DURATION
        samples_per_segment = int(SAMPLES_PER_TRACK / self.num_segments)
        num_mfcc_vectors_per_segment = math.ceil(samples_per_segment / self.hop_length)
        signal, sample_rate = librosa.load(file_path, sr=self.SAMPLE_RATE)
        X=list()
        for d in range(self.num_segments):
            start = samples_per_segment * d
            finish = start + samples_per_segment
            mfcc = librosa.feature.mfcc(y=signal[start:finish], sr=sample_rate, n_mfcc=self.num_mfcc, n_fft=self.n_fft, hop_length=self.hop_length)
            mfcc = mfcc.T
            if(len(mfcc) == num_mfcc_vectors_per_segment):
                 X.append(mfcc.tolist())
        X=np.array(X)
        X = X[..., np.newaxis]
        X=X[0]
        X = X[np.newaxis, ...]
        return X
    
    def predict_genre(self,file_path,model):     
        try:
            X=self.extract_features(file_path)
        except:
            print("Features couldn't be extracted")
            return None
        print("Features extracted")
        prediction = model.predict(X)
        prediction=list(prediction[0])
        genre_probability_dict=dict(zip(self.genre_list, prediction))
        print("Genre probabilties computed")
        return genre_probability_dict