import os
from flask import Flask, jsonify, request
import requests
app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()

TMDB_API_KEY = os.getenv('API_KEY')
if not TMDB_API_KEY:
    raise SystemExit('Cle API manquante, ajoute là dans ton .env')

TMDB_BASE_URL = "https://api.themoviedb.org/3"

@app.route('/', methods=['GET'])
def test():
    return jsonify({'message' : 'It works !'})

@app.route('/api/movie/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": 'fr-FR',
    }
    response = requests.get(url, params = params)
    # L'id 550 retourne Fight Club
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=8080)
