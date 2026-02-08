import sqlite3
import json
import os

DB_FILE = "db_test.sqlite3"
OUTPUT_FILE = "export_pistes.txt"

def get_data_as_dict(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    # Récupérer les noms des colonnes
    columns = [description[0] for description in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results

def run_export():
    if not os.path.exists(DB_FILE):
        print(f"❌ Erreur : {DB_FILE} introuvable.")
        return

    print(f"Connexion à {DB_FILE}...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        
        # --- 1. TABLE CONTACTS ---
        print("Récupération des CONTACTS...")
        contacts = get_data_as_dict(cursor, "candidatures_contact")
        
        f.write("="*60 + "\n")
        f.write("1. TABLE : candidatures_contact\n")
        f.write("="*60 + "\n")
        f.write(json.dumps(contacts, indent=4, ensure_ascii=False))
        f.write("\n\n")

        # --- 2. TABLE PISTES ---
        print("Récupération des PISTES...")
        pistes = get_data_as_dict(cursor, "candidatures_pistecandidature")
        
        f.write("="*60 + "\n")
        f.write("2. TABLE : candidatures_pistecandidature\n")
        f.write("="*60 + "\n")
        f.write(json.dumps(pistes, indent=4, ensure_ascii=False))
        f.write("\n\n")

        # --- 3. TABLE DE LIAISON (IDs seulement) ---
        print("Récupération des LIAISONS (Table Pivot)...")
        liaisons = get_data_as_dict(cursor, "candidatures_pistecandidature_contacts")
        
        f.write("="*60 + "\n")
        f.write("3. TABLE : candidatures_pistecandidature_contacts (IDs bruts)\n")
        f.write("="*60 + "\n")
        f.write(json.dumps(liaisons, indent=4, ensure_ascii=False))
        f.write("\n\n")

        # --- 4. VUE HUMAINE (Bonus : Les noms au lieu des IDs) ---
        print("Génération de la vue lisible...")
        f.write("="*60 + "\n")
        f.write("4. VUE HUMAINE (Qui est lié à quoi ?)\n")
        f.write("="*60 + "\n")
        
        sql_readable = """
            SELECT 
                p.entreprise,
                p.poste_cible,
                c.prenom || ' ' || c.nom as contact_nom,
                c.poste_occupe as contact_role
            FROM candidatures_pistecandidature_contacts lien
            JOIN candidatures_pistecandidature p ON lien.pistecandidature_id = p.id
            JOIN candidatures_contact c ON lien.contact_id = c.id
        """
        cursor.execute(sql_readable)
        readable_rows = cursor.fetchall()
        
        if not readable_rows:
            f.write("Aucune liaison trouvée.\n")
        
        for row in readable_rows:
            line = f"🏢 Piste : {row[0]} ({row[1]})  <--->  👤 Contact : {row[2]} ({row[3]})\n"
            print(line.strip()) # Affiche aussi dans le terminal
            f.write(line)

    conn.close()
    print(f"\n✅ Terminé ! Toutes les données sont dans le fichier : {OUTPUT_FILE}")

if __name__ == "__main__":
    run_export()