import streamlit as st
from api import app

TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w342"

st.title("Infos film")

movie_id = st.number_input("ID TMDB", min_value=1, value=550, step=1)

# Appelle la route Flask directement, sans lancer de serveur ni ouvrir de port.
response = app.test_client().get(f"/api/movie/{movie_id}")
data = response.get_json()

if response.status_code != 200:
    st.error(data["description"])
    st.stop()

st.header(data["title"])

if data.get("poster_path"):
    st.image(f"{TMDB_IMAGE_URL}{data['poster_path']}")

st.write(data.get("overview") or "Pas de résumé disponible.")
st.caption(f"Sortie : {data.get('release_date') or 'inconnue'}")
st.metric("Note moyenne", f"{data.get('vote_average', 0):.1f} / 10")
