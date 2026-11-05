# TP API Python

API Flask qui expose les informations d'un film à partir de [TMDB](https://www.themoviedb.org/), avec une interface Streamlit.

**Application en ligne :** https://tp-api-gabriel.streamlit.app/

## Dépendances

| Paquet | Version | Rôle |
| --- | --- | --- |
| `flask[async]` | 3.1.3 | API HTTP, routes asynchrones |
| `Flask-Caching` | 2.5.1 | Cache des réponses |
| `httpx` | 0.28.1 | Appels à l'API TMDB |
| `python-dotenv` | 1.2.4 | Chargement du fichier `.env` |
| `pandas` | 3.1.1 | Import des films dans SQLite (`data.py`) |
| `streamlit` | 1.66.1 | Interface web |

## Installation

Il faut Python 3 et une clé API TMDB.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Renseigner ensuite la clé dans `.env` :

```
API_KEY = votre_cle_tmdb
```

## Lancement

Interface Streamlit, sur http://localhost:8501 :

```bash
streamlit run streamlit_app.py
```

Elle appelle directement les routes Flask : il n'est pas nécessaire de lancer l'API à côté.

API seule, sur http://localhost:8080 :

```bash
python api.py
```

| Route | Description |
| --- | --- |
| `GET /` | Vérifie que l'API répond |
| `GET /api/movie/<id>` | Détails d'un film en français, mis en cache une heure |

Exemple avec l'identifiant 550, qui correspond à Fight Club :

```bash
curl http://localhost:8080/api/movie/550
```

Les erreurs sont renvoyées en JSON, avec les champs `code`, `name` et `description`.

## Tests

```bash
python -m unittest test_cache -v
```

Les tests vérifient le comportement du cache. TMDB est simulé : ils ne font aucun appel réseau et ne demandent pas de clé API.

## Base de données

`data.py` lit `movies.json`, génère `movies_array.json` et remplit la table `nom_de_la_table` de `data.db` :

```bash
python data.py
```

`update_data.py` télécharge le dernier [export quotidien de TMDB](https://developer.themoviedb.org/docs/daily-id-exports) dans `movies.json`, puis lance `data.py`. Il ne demande pas de clé API :

```bash
python update_data.py
```

Pour le lancer tous les 3 mois (le 1er janvier, avril, juillet et octobre à 6 h), ajouter cette ligne avec `crontab -e` :

```
0 6 1 */3 * cd /Users/gabriel/Documents/code/api_python && .venv/bin/python update_data.py
```

L'API et l'interface n'utilisent pas cette base.
