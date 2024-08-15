import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# Spotify API credentials
client_id = ''
client_secret = ''
redirect_uri = ''

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope='user-library-read',
    cache_path=".cache"  # Set cache_path to manage tokens or None if you don't want to cache tokens
))

# Read history CSV
history = pd.read_csv(r'C:\Users\msaha\OneDrive\Desktop\music_Rec\cleaned_combined_history.csv')

# Function to get track ID
def get_track_id(track_name, artist_name):
    results = sp.search(q=f'track:{track_name} artist:{artist_name}', type='track', limit=1)
    tracks = results['tracks']['items']
    return tracks[0]['id'] if tracks else None

# Batch processing function
def fetch_audio_features(track_ids):
    try:
        features = sp.audio_features(track_ids)  # Pass track_ids as a list
        return features
    except spotipy.exceptions.SpotifyException as e:
        print(f"Spotify API error: {e}")
        time.sleep(60)  # Wait for 60 seconds and retry in case of rate limit
        return fetch_audio_features(track_ids)
    except Exception as e:
        print(f"Error fetching audio features: {e}")
        return None

audio_features = []
track_id_map = {}

# Collect track IDs
track_ids = []
for index, row in history.iterrows():
    track_id = get_track_id(row['trackName'], row['artistName'])
    if track_id:
        track_ids.append(track_id)
        track_id_map[track_id] = (row['trackName'], row['artistName'])  # Map track ID to song details
        print(f"Track {index + 1} processed")
    
    # Process in batches of 100 (0-indexed, so len(track_ids) == 100)
    if len(track_ids) == 100:
        features = fetch_audio_features(track_ids)
        if features:
            valid_features = [f for f in features if f is not None]  # Filter out None values
            audio_features.extend(valid_features)
        track_ids = []
        time.sleep(1)  #  handle rate limits

# Fetch any remaining tracks
if track_ids:
    features = fetch_audio_features(track_ids)
    if features:
        valid_features = [f for f in features if f is not None]  # Filter out None values
        audio_features.extend(valid_features)

# Convert to DataFrame
if audio_features:
    audio_features_df = pd.DataFrame(audio_features)
    
    # Map track ID back to the original track and artist names
    audio_features_df['trackName'] = audio_features_df['id'].apply(lambda x: track_id_map[x][0])
    audio_features_df['artistName'] = audio_features_df['id'].apply(lambda x: track_id_map[x][1])
    
    # Merge with the original history DataFrame
    features_df = pd.merge(history, audio_features_df, on=['trackName', 'artistName'], how='left')
    
    # Save the final DataFrame
    features_df.to_csv('features.csv', index=False)
else:
    print("No valid audio features were retrieved.")
