import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import joblib

# Set up Spotify credentials
client_id = "d3d1c7007f124da1b57411f7cbdafb3f"
client_secret = "ed1ebccfb0b7479884d4034e03ef70e0"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load the model (update the path accordingly)
model = joblib.load('spotify_model.pkl')  # Update this path

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Top Songs by Year", "Mood-Based Recommendations", "Track-Based Recommendations", "Visualizations"])

# Functions
def get_recommendations(track_name):
    """Fetch recommendations based on a track name."""
    try:
        results = sp.search(q=track_name, type='track')
        if len(results['tracks']['items']) == 0:
            return None, None, None
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        track_popularity = track['popularity']
        track_features = sp.audio_features([track_uri])[0]  # Get track audio features
        
        # Get recommended tracks
        recommendations = sp.recommendations(seed_tracks=[track_uri])['tracks']
        return track_popularity, track_features, recommendations
    except Exception as e:
        st.error(f"Error fetching recommendations: {str(e)}")
        return None, None, None

def get_top_tracks_by_year_range(start_year, end_year):
    """Fetch the top tracks from Spotify within the given year range."""
    try:
        top_tracks = sp.search(q=f"year:{start_year}-{end_year}", type='track', limit=10)['tracks']['items']
        return top_tracks
    except Exception as e:
        st.error(f"Error fetching top tracks: {str(e)}")
        return None

def get_recommendations_by_mood(mood, start_year=None, end_year=None):
    """Fetch recommendations based on the selected mood."""
    mood_to_features = {
        'Happy': {'valence': 0.8, 'energy': 0.7},
        'Sad': {'valence': 0.2, 'energy': 0.3},
        'Energetic': {'energy': 0.9, 'danceability': 0.8}
    }
    features = mood_to_features.get(mood, None)
    if not features:
        return None
    try:
        recommendations = sp.recommendations(seed_genres=['pop', 'indie'], limit=10,  # Updated to include 'indie' for Indian Pop
                                             target_valence=features.get('valence', None),
                                             target_energy=features.get('energy', None),
                                             target_danceability=features.get('danceability', None),
                                             min_year=start_year, max_year=end_year)['tracks']
        return recommendations
    except Exception as e:
        st.error(f"Error fetching mood-based recommendations: {str(e)}")
        return None

# Home Page
if page == "Home":
    st.title("🎵 Music Recommendation System")
    st.write("Welcome to the music recommendation system! Use the sidebar to navigate between different features.")
    
# Top Songs by Year Page
if page == "Top Songs by Year":
    st.title("Top Songs by Year Range")
    start_year, end_year = st.slider("Select Year Range", min_value=1960, max_value=2023, value=(2000, 2023), step=1)
    st.write(f"Fetching the top songs from {start_year} to {end_year}...")
    top_tracks = get_top_tracks_by_year_range(start_year, end_year)
    if top_tracks:
        st.write(f"### Top Songs from {start_year} to {end_year}:")
        for track in top_tracks:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(track['album']['images'][0]['url'], width=100)
            with col2:
                st.write(f"**{track['name']}** by {track['artists'][0]['name']}")
                if track['preview_url']:
                    st.audio(track['preview_url'], format="audio/mp3")
    else:
        st.write(f"No top songs found for the selected range {start_year} - {end_year}.")

# Mood-Based Recommendations Page
if page == "Mood-Based Recommendations":
    st.title("Mood-Based Recommendations")
    st.write("### How are you feeling today? Click an emoji to get recommendations based on your mood!")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("😊 Happy"):
            mood = "Happy"
    with col2:
        if st.button("😢 Sad"):
            mood = "Sad"
    with col3:
        if st.button("⚡ Energetic"):
            mood = "Energetic"
    if 'mood' in locals():
        st.write(f"Fetching songs that match your {mood} mood...")
        recommendations = get_recommendations_by_mood(mood)
        if recommendations:
            st.write(f"### Recommended {mood} Songs:")
            for track in recommendations:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(track['album']['images'][0]['url'], width=100)
                with col2:
                    st.write(f"**{track['name']}** by {track['artists'][0]['name']}")
                    if track['preview_url']:
                        st.audio(track['preview_url'], format="audio/mp3")

# Track-Based Recommendations Page
if page == "Track-Based Recommendations":
    st.title("Track-Based Recommendations")
    track_name = st.text_input("Enter a song name:")
    if track_name.strip() == "":
        st.write("Enter the title of a song you love for personalized recommendations!")
    else:
        with st.spinner('Fetching recommendations...'):
            track_popularity, track_features, recommendations = get_recommendations(track_name)
        if recommendations:
            st.write(f"Popularity of '{track_name}': {track_popularity}")
            st.write("Recommended songs based on your selection:")
            for track in recommendations:
                st.write(f"{track['name']} by {track['artists'][0]['name']}")
                st.image(track['album']['images'][0]['url'], width=150)
                if track['preview_url']:
                    st.audio(track['preview_url'], format="audio/mp3")

# Visualizations Page
if page == "Visualizations":
    st.title("Visualizations")
    
    # Load and display the saved images
    st.image('Images/total_streams_by_year.png', caption='Total Streams by Released Year', use_column_width=True)
    st.image('Images/top_10_artists.png', caption='Top 10 Artists by Total Streams', use_column_width=True)
    st.image('Images/danceability_vs_energy.png', caption='Danceability vs Energy', use_column_width=True)
    st.image('Images/distribution_of_streams.png', caption='Distribution of Streams', use_column_width=True)
    st.image('Images/acousticness_by_key.png', caption='Acousticness by Key', use_column_width=True)
