import sqlite3

# Connexion
con = sqlite3.connect("db_test.sqlite3")
cur = con.cursor()

# Lister les tables
res = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", res.fetchall())

# Lire des données (exemple sur la table Candidature)
# Note : Le nom de la table est souvent 'applabel_modelname' dans Django
try:
    res = cur.execute("SELECT id, entreprise, poste FROM candidatures_candidature LIMIT 5")
    for row in res.fetchall():
        print(row)
except sqlite3.OperationalError:
    print("Table non trouvée, vérifiez le nom exact avec la commande précédente.")

con.close()