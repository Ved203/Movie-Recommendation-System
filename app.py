import os
import download_models
import pandas as pd
import pickle
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="FilemPick - AI Movie Recommender",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    background: linear-gradient(135deg,#050816,#0b1120);
    color: white;
}

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
    width: 280px !important;
}

.sidebar-title {
    font-size: 40px;
    font-weight: 700;
    color: #7c5cff;
}

.sidebar-subtitle {
    color: #9ca3af;
    font-size: 15px;
    margin-bottom: 40px;
}

.hero-title {
    font-size: 80px;
    font-weight: 600;
    line-height: 1;
}

.gradient-text {
    background: linear-gradient(90deg,#7c5cff,#4f8cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 24px;
    color: white;
}

.hero-description {
    color: #9ca3af;
    font-size: 18px;
    max-width: 700px;
    line-height: 1.7;
}

.stButton > button {
    background: linear-gradient(90deg,#7c5cff,#4f8cff);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-weight: 600;
    width: 100%;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 8px 20px rgba(124,92,255,0.4);
}

.movie-container {
    background: rgba(17,24,39,0.85);
    padding: 12px;
    border-radius: 18px;
    margin-bottom: 20px;
    transition: 0.3s ease;
    border: 1px solid rgba(255,255,255,0.08);
}

.movie-container:hover {
    transform: translateY(-6px);
    box-shadow: 0px 10px 25px rgba(124,92,255,0.25);
}

.movie-title {
    font-size: 17px;
    font-weight: 700;
    color: white;
    margin-top: 10px;
    min-height: 50px;
}

.section-title {
    font-size: 32px;
    font-weight: 700;
    margin-top: 30px;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================

if "recent_movies" not in st.session_state:
    st.session_state.recent_movies = []

# =====================================================
# API SESSION
# =====================================================

session = requests.Session()

retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429,500,502,503,504]
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("https://", adapter)

#```python
# =====================================================
# LOAD DATA
# =====================================================

BASE_DIR = os.path.dirname(__file__)

movie_path = os.path.join(
    BASE_DIR,
    "saved_models",
    "movie_dict.pkl"
)

similarity_path = os.path.join(
    BASE_DIR,
    "saved_models",
    "similarity.pkl"
)

@st.cache_resource
def load_data():

    movies_dict = pickle.load(
        open(movie_path, "rb")
    )

    movies = pd.DataFrame(movies_dict)

    similarity = pickle.load(
        open(similarity_path, "rb")
    )

    return movies, similarity

movies, similarity = load_data()

# =====================================================
# TMDB API
# =====================================================

API_KEY = st.secrets["TMDB_API_KEY"]

@st.cache_data
def fetch_movie_details(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    try:

        response = session.get(url, timeout=10)

        data = response.json()

        poster_path = data.get("poster_path")

        genres = [
            genre['name']
            for genre in data.get("genres", [])
        ]

        return {

            "poster":
            f"https://image.tmdb.org/t/p/w500{poster_path}"
            if poster_path
            else "https://placehold.co/500x750",

            "rating":
            round(data.get("vote_average", 0), 1),

            "year":
            data.get("release_date", "")[:4],

            "genres":
            ", ".join(genres),

            "trailer":
            f"https://www.themoviedb.org/movie/{movie_id}"
        }

    except:

        return {
            "poster": "https://placehold.co/500x750",
            "rating": "N/A",
            "year": "N/A",
            "genres": "N/A",
            "trailer": "#"
        }

# =====================================================
# RECOMMEND FUNCTION
# =====================================================

def recommend(movie):

    index = movies[movies['title'] == movie].index[0]

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movies = []

    for i in distances[1:7]:

        movie_data = movies.iloc[i[0]]

        details = fetch_movie_details(
            movie_data.movie_id
        )

        recommended_movies.append({

            "title": movie_data.title,
            "poster": details["poster"],
            "rating": details["rating"],
            "year": details["year"],
            "genres": details["genres"],
            "trailer": details["trailer"]
        })

    return recommended_movies

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown("""
<div class="sidebar-title">
FilmPick
</div>

<div class="sidebar-subtitle">
Smart Movie Discovery Platform
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Recent Searches",
        
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "AI-powered movie recommendation system using Machine Learning."
)

# =====================================================
# HOME
# =====================================================

if menu == "Home":

    st.markdown("""
    <div class="hero-title" style="margin-top:40px;">
    Welcome to <br>
    <span class="gradient-text">
    FilmPick
    </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-subtitle">
    Smart Recommendations. Endless Entertainment.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-description">
    Discover movies tailored to your taste using AI-powered recommendations.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    movie_list = movies['title'].values

    selected_movie = st.selectbox(
        "Search or select a movie",
        movie_list
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Get Recommendations"):

        st.session_state.recent_movies.append(
            selected_movie
        )

        with st.spinner(
            "Finding movies..."
        ):

            recommendations = recommend(
                selected_movie
            )

        st.markdown("""
        <div class="section-title">
        Recommended Movies
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(6)

        for idx, movie in enumerate(recommendations):

            with cols[idx % 6]:

                st.markdown(
                    '<div class="movie-container">',
                    unsafe_allow_html=True
                )

                st.image(
                    movie['poster'],
                    width="stretch"
                    
                )

                st.markdown(
                    f'<div class="movie-title">{movie["title"]}</div>',
                    unsafe_allow_html=True
                )

                st.caption(f"⭐ {movie['rating']}")
                st.caption(f"📅 {movie['year']}")
                st.caption(f"🎭 {movie['genres']}")

                st.link_button(
                    "View Details",
                    movie['trailer']
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )



# =====================================================
# RECOMMENDATION HISTORY
# =====================================================

elif menu == "Recent Searches":

    st.markdown(
        '<div class="section-title">Recently Searched</div>',
        unsafe_allow_html=True
    )

    if st.session_state.recent_movies:

        for movie in reversed(
            st.session_state.recent_movies[-10:]
        ):

            st.write(f"• {movie}")

    else:

        st.info("No recent searches yet.")

