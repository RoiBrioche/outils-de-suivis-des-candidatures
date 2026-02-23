import sqlite3
import os

# Nom du fichier de base de données
db_file = "db_test.sqlite3"


def lister_tables():
    # 1. Vérifier si le fichier existe
    if not os.path.exists(db_file):
        print(f"❌ Erreur : Le fichier '{db_file}' n'existe pas.")
        print("   Assure-toi d'être dans le bon dossier.")
        return

    print(f"📂 Connexion à : {db_file}\n")

    # 2. Connexion
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 3. Récupérer la liste des tables (exclure les tables internes de sqlite)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        )
        tables = cursor.fetchall()

        if not tables:
            print("Aucune table trouvée.")
            return

        print(f"{'NOM DE LA TABLE':<40} | {'LIGNES':<10}")
        print("-" * 55)

        # 4. Parcourir et compter les lignes
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]

                # Petit bonus visuel : mettre en évidence tes tables "candidatures"
                prefix = "⭐ " if table_name.startswith("candidatures_") else "   "
                print(f"{prefix}{table_name:<37} | {count:>6}")

            except sqlite3.OperationalError as e:
                print(f"   {table_name:<37} | Erreur lecture")

        print("-" * 55)
        print(f"\n✅ Total : {len(tables)} tables trouvées.")

    except sqlite3.Error as e:
        print(f"❌ Erreur SQLite : {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    lister_tables()
