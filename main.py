from flask import Flask, render_template, request
import pickle
import requests

app = Flask(__name__)

# Load models
similarity = pickle.load(open('models/similarity.pkl', 'rb'))
movies_df = pickle.load(open('models/movies.pkl', 'rb'))
movie_titles = movies_df['title'].values

def fetch_poster_path(movie_name, api_key):
    # Define the URL for the TMDb Search API
    url = "https://api.themoviedb.org/3/search/movie"

    # Define the query parameters
    params = {"api_key": api_key, "query": movie_name}

    # Make the API request
    response = requests.get(url, params=params)

    # Check the response status
    if response.status_code == 200:
        data = response.json()
        # Check if there are results
        if data.get("results"):
            # Get the first result
            first_movie = data["results"][0]
            # Extract the poster path
            poster_path = first_movie.get("poster_path")
            if poster_path:
                full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                return full_poster_url
            else:
                return "Poster path not available."
        else:
            return "No movies found for the given name."
    else:
        return f"Error: {response.status_code}, Message: {response.text}"

api_key = "c740e63ee809f400e29708daf0ffcba8"

# Recommendation logic
def get_recommendations(movie):
    # Check if the movie exists in the dataset
    if movie not in movies_df['title'].values:
        return [f"Movie '{movie}' not found!"], []

    # Get the index of the movie
    movie_index = movies_df[movies_df['title'] == movie].index[0]

    # Get the similarity scores for the movie
    distances = similarity[movie_index]

    # Get the top 6 similar movies (excluding itself)
    movie_indices = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]
    
    poster_path = []
    # Get movie titles
    recommended_movies = [movies_df.iloc[i[0]]['title'] for i in movie_indices]
    for i in recommended_movies:
        poster_path.append(fetch_poster_path(i, api_key))  # Fetch poster for each recommended movie

    return recommended_movies, poster_path

# Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []  # Default value for recommendations in case of GET request
    path = []  # Default value for paths in case of GET request
    if request.method == 'POST':
        selected_option = request.form.get('selected_option')
        if not selected_option:
            return "No movie selected!", 400
        
        recommendations, path = get_recommendations(selected_option)
    
    # Pass both movie_titles and recommendations to the template
    return render_template('index.html', items=movie_titles, recommendations=recommendations, path=path)

if __name__ == "__main__":
    app.run(debug=True)
