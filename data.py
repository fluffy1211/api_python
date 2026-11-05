import json
import sqlite3
import pandas as pd

# movies.json est au format NDJSON : un objet JSON par ligne.
with open('movies.json', 'r', encoding='utf-8') as f:
  array_json = [json.loads(line) for line in f if line.strip()]

# (Optionnel) Sauvegarder le format array JSON propre si besoin
with open('movies_array.json', 'w', encoding='utf-8') as f:
  json.dump(array_json, f, ensure_ascii=False, indent=4)

# 3. Créer un DataFrame Pandas à partir de l'array JSON
df = pd.DataFrame(array_json)

# 4. Connexion et injection dans la base SQLite
conn = sqlite3.connect('data.db')

# 'to_sql' crée la table et insère les données.
# if_exists='replace' remplace la table si elle existe déjà (choisissez 'append' ou 'fail' selon le besoin).
df.to_sql('nom_de_la_table', conn, if_exists='replace', index=False)

conn.close()
print(
    'Les données ont été converties et injectées avec succès dans SQLite !'
)