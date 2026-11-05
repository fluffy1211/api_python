import os
from flask import Flask, abort, jsonify
import requests
from werkzeug.exceptions import HTTPException
app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv()

TMDB_API_KEY = os.getenv('API_KEY')
if not TMDB_API_KEY:
    raise SystemExit('Cle API manquante, ajoute là dans ton .env')

TMDB_BASE_URL = "https://api.themoviedb.org/3"

def error_response(code, name, description):
    return jsonify({"code": code, "name": name, "description": description}), code

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """Retourne du JSON au lieu du HTML pour les erreurs HTTP."""
    return error_response(e.code, e.name, e.description)

@app.errorhandler(requests.exceptions.Timeout)
def handle_timeout(e):
    return error_response(504, "Gateway Timeout", "TMDB n'a pas répondu à temps.")

@app.errorhandler(requests.exceptions.RequestException)
def handle_request_exception(e):
    return error_response(502, "Bad Gateway", "Impossible de contacter TMDB.")

@app.errorhandler(Exception)
def handle_unexpected_exception(e):
    app.logger.exception(e)
    return error_response(500, "Internal Server Error", "Une erreur inattendue est survenue.")

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
    # L'id 550 retourne Fight Club
    response = requests.get(url, params=params, timeout=5)

    if response.status_code == 404:
        abort(404, description=f"Film {movie_id} introuvable.")
    if response.status_code == 401:
        abort(502, description="Clé API TMDB invalide.")
    if response.status_code == 429:
        abort(503, description="Limite de requêtes TMDB atteinte.")
    if not response.ok:
        abort(502, description="Réponse inattendue de TMDB.")

    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=8080)
