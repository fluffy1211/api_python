"""Vérifie le cache de /api/movie/<id>, sans jamais appeler le vrai TMDB.

Lancer avec : .venv/bin/python -m unittest test_cache -v
"""
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

os.environ.setdefault("API_KEY", "cle-de-test")

from api import app, cache


def fake_tmdb(status_code=200, payload=None):
    """Remplace httpx.AsyncClient : on compte les appels via client.get."""
    response = MagicMock(
        status_code=status_code,
        is_success=status_code < 400,
    )
    response.json.return_value = payload or {"id": 550, "title": "Fight Club"}

    client = MagicMock()
    client.get = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    return client


class CacheTest(unittest.TestCase):
    def setUp(self):
        cache.clear()
        self.http = app.test_client()

    def test_deuxieme_appel_servi_par_le_cache(self):
        tmdb = fake_tmdb()
        with patch("app.httpx.AsyncClient", return_value=tmdb):
            first = self.http.get("/api/movie/550")
            second = self.http.get("/api/movie/550")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json(), second.get_json())
        self.assertEqual(tmdb.get.await_count, 1)

    def test_chaque_film_a_sa_propre_entree(self):
        tmdb = fake_tmdb()
        with patch("app.httpx.AsyncClient", return_value=tmdb):
            self.http.get("/api/movie/550")
            self.http.get("/api/movie/551")

        self.assertEqual(tmdb.get.await_count, 2)

    def test_le_404_est_mis_en_cache(self):
        tmdb = fake_tmdb(status_code=404)
        with patch("app.httpx.AsyncClient", return_value=tmdb):
            first = self.http.get("/api/movie/999")
            second = self.http.get("/api/movie/999")

        self.assertEqual(first.status_code, 404)
        self.assertEqual(second.status_code, 404)
        self.assertEqual(tmdb.get.await_count, 1)

    def test_le_503_n_est_pas_mis_en_cache(self):
        # TMDB répond 429 (limite atteinte), notre API renvoie 503
        with patch("app.httpx.AsyncClient", return_value=fake_tmdb(status_code=429)):
            first = self.http.get("/api/movie/550")

        # TMDB est rétabli : la requête suivante doit réussir
        with patch("app.httpx.AsyncClient", return_value=fake_tmdb()):
            second = self.http.get("/api/movie/550")

        self.assertEqual(first.status_code, 503)
        self.assertEqual(second.status_code, 200)

    def test_expiration_apres_une_heure(self):
        tmdb = fake_tmdb()
        with patch("app.httpx.AsyncClient", return_value=tmdb):
            with patch("cachelib.simple.time", return_value=1_000_000):
                self.http.get("/api/movie/550")

            # Juste avant l'heure : toujours en cache
            with patch("cachelib.simple.time", return_value=1_000_000 + 3599):
                self.http.get("/api/movie/550")
            self.assertEqual(tmdb.get.await_count, 1)

            # Juste après l'heure : le cache a expiré, on rappelle TMDB
            with patch("cachelib.simple.time", return_value=1_000_000 + 3601):
                self.http.get("/api/movie/550")
            self.assertEqual(tmdb.get.await_count, 2)


if __name__ == "__main__":
    unittest.main()
