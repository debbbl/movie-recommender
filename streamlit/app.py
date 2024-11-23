import streamlit as st
import pickle
import os
import gzip
import pandas as pd
import requests
print("Current working directory:", os.getcwd())
print("Files in current directory:", os.listdir(os.getcwd()))
# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))
movie_model_path = os.path.join(base_dir, 'movie_dict.pkl.gz')
print(movie_model_path)

movie_similarity_model_path = os.path.join(base_dir, 'movie_similarity.pkl.gz')
print(movie_similarity_model_path)

# Loading the compressed pickle files with gzip
with gzip.open(movie_model_path, 'rb') as f:
    movie_list = pickle.load(f)

# Converting movie list to DataFrame
movies = pd.DataFrame(movie_list)
movie_title = movies['title'].values

with gzip.open(movie_similarity_model_path, 'rb') as f:
    movie_similarity = pickle.load(f)

# Fetch movie poster and details
def fetch_movie_details(movie_id):
    api_key = "72297ce8cd122a7616cdaf35c27d3200"
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    response = requests.get(url)
    data = response.json()
    poster_url = "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', '')
    overview = data.get('overview', 'No overview available.')
    release_date = data.get('release_date', 'N/A')
    rating = data.get('vote_average', 'N/A')
    return poster_url, overview, release_date, rating

# Suggest movies
def movie_suggestion(movie_name):
    movie_index = movies[movies['title'] == movie_name].index[0]
    distances = movie_similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    suggested_movies = []
    suggested_movie_details = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster_url, overview, release_date, rating = fetch_movie_details(movie_id)
        suggested_movie_details.append({
            "title": movies.iloc[i[0]].title,
            "poster": poster_url,
            "overview": overview,
            "release_date": release_date,
            "rating": rating
        })
    return suggested_movie_details

# Page Styling
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://source.unsplash.com/1600x900/?movies,cinema");
        background-size: cover;
    }
    h1 {
        color: white;
        text-align: center;
    }
    .movie-card {
        padding: 10px;
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Website title
st.markdown("<h1 style='color: black; font-size: 30px;'>🎬 Movie Recommendation System 🎥</h1>", unsafe_allow_html=True)

# Movie selection
input_movie_title = st.selectbox("Search for a movie:", movie_title)

if st.button('Suggest Movies'):
    suggestions = movie_suggestion(input_movie_title)

    st.markdown("<h2>Recommended Movies:</h2>", unsafe_allow_html=True)
    for suggestion in suggestions:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(suggestion['poster'], use_column_width=True)
        with col2:
            st.markdown(f"""
                <div class="movie-card">
                    <h3>{suggestion['title']}</h3>
                    <p><b>Release Date:</b> {suggestion['release_date']}</p>
                    <p><b>Rating:</b> {suggestion['rating']} ⭐</p>
                    <p><b>Overview:</b> {suggestion['overview']}</p>
                </div>
            """, unsafe_allow_html=True)


