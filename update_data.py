"""Met à jour data.db avec le dernier export quotidien de TMDB.

Lancer avec : .venv/bin/python update_data.py
Tous les 3 mois avec cron, voir le README.
"""
import gzip
import runpy
from datetime import datetime, timedelta, timezone

import httpx

# L'export du jour peut ne pas être encore publié : on prend celui de la veille.
yesterday = datetime.now(timezone.utc) - timedelta(days=1)
url = f"https://files.tmdb.org/p/exports/movie_ids_{yesterday:%m_%d_%Y}.json.gz"

response = httpx.get(url, timeout=60)
response.raise_for_status()

# Décompressé avant d'ouvrir le fichier : en cas d'erreur, movies.json reste intact.
movies = gzip.decompress(response.content)
with open('movies.json', 'wb') as f:
    f.write(movies)

# data.py recharge movies.json dans data.db.
runpy.run_path('data.py')
