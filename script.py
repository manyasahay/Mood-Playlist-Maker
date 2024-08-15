from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__, template_folder='templates')

# Spotify API credentials
client_id = ''
client_secret = ''
redirect_uri = ''

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope='playlist-modify-public playlist-modify-private',
    cache_path=".cache"  # Set cache_path to manage tokens or None if you don't want to cache tokens
))

# Load your data
data_mood = pd.read_csv(r'C:\Users\msaha\OneDrive\Desktop\music_Rec\features_mood.csv')

@app.route("/")
def home():
    return render_template("webpage.html", result="")

@app.route("/run")
def run_script():
    action = request.args.get("action")
    mood_labels = {'sad': 2, 'happy': 0, 'energy': 1}
    
    if action in mood_labels:
        mood = mood_labels[action]
        songs = get_similar_songs(mood)
        playlist_id = create_playlist_with_songs(songs)
        result = {"message": f"Running script for {action} mood...", "songs": songs, "playlist_id": playlist_id}
    else:
        result = {"message": "Unknown action", "songs": [], "playlist_id": None}
    
    return jsonify(result)

def get_similar_songs(mood, num_songs=15):
    mood_songs = data_mood[data_mood['mood'] == mood]
    if len(mood_songs) < 15:
        return mood_songs[['trackName', 'artistName']].to_dict(orient='records')

    features = mood_songs[['danceability', 'loudness', 'speechiness', 'acousticness', 'valence']]
    similarity_matrix = cosine_similarity(features)
    similarity_scores = similarity_matrix.sum(axis=1)
    top_indices = np.argsort(similarity_scores)[-num_songs:]

    top_songs = mood_songs.iloc[top_indices][['trackName', 'artistName']]
    return top_songs.to_dict(orient='records')

def create_playlist_with_songs(songs):
    # Get the user ID
    user_id = sp.current_user()['id']

    # Create a new playlist
    playlist = sp.user_playlist_create(user=user_id, name="My Mood Playlist", public=False)
    playlist_id = playlist['id']

    # Add tracks to the playlist
    track_ids = []
    for song in songs:
        track_id = get_track_id(song['trackName'], song['artistName'])
        if track_id:
            track_ids.append(track_id)
    
    if track_ids:
        sp.playlist_add_items(playlist_id, track_ids)
    
    return playlist_id

def get_track_id(track_name, artist_name):
    results = sp.search(q=f'track:{track_name} artist:{artist_name}', type='track', limit=1)
    tracks = results['tracks']['items']
    return tracks[0]['id'] if tracks else None

if __name__ == '__main__':
    app.run(debug=True)
