# Suivi des candidatures (MVP)

## 📌 Présentation

**Suivi des candidatures** est une application Django MVP pour gérer et suivre vos candidatures professionnelles.  
Elle permet de :  
- Ajouter, modifier et supprimer des candidatures (CRUD)  
- Consulter et filtrer les candidatures sur une interface principale  
- Gérer les périodes de candidature  
- Visualiser des statistiques simples  

Le projet utilise **Windsurf** pour faciliter le développement assisté par IA et inclut la documentation **Obsidian** pour fournir le contexte nécessaire à l’IA.

---

## 🛠️ Technologies

- **Backend** : Python + Django  
- **Base de données** : SQLite (MVP)  
- **Outils IA / Dev** : Windsurf  
- **Documentation** : Obsidian (Markdown)

---

## 📁 Arborescence du projet

```
suivi-candidatures-mvp/
│
├─ README.md
├─ LICENSE
├─ .gitignore
├─ requirements.txt
├─ pyproject.toml
├─ obsidian-docs/           # documentation projet pour IA
│   ├─ 00-introduction.md
│   ├─ 01-schema-donnees.md
│   ├─ 02-architecture-technique.md
│   └─ 03-validation-erreurs.md
├─ src/
│   ├─ manage.py
│   ├─ config/              # settings, urls
│   └─ app/                 # apps Django
│       ├─ models.py
│       ├─ views.py
│       ├─ serializers.py
│       └─ ...
├─ tests/
└─ data/                    # données de test
```

---

## 🚀 Installation

1. **Cloner le dépôt**  
```bash
git clone https://github.com/<votre-utilisateur>/suivi-candidatures-mvp.git
cd suivi-candidatures-mvp
```

2. **Créer un environnement virtuel**  
```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

3. **Installer les dépendances**  
```bash
pip install -r requirements.txt
```

4. **Initialiser la base de données**  
```bash
python manage.py migrate
```

5. **Lancer le serveur de développement**  
```bash
python manage.py runserver
```

---

## 🧠 Utilisation avec Windsurf

Windsurf permet d’utiliser l’IA pour :  
- Générer du code basé sur la documentation Obsidian  
- Vérifier la cohérence du code avec l’architecture définie  
- Automatiser certaines tâches répétitives (CRUD, validation, tests)  

💡 **Conseil** : placez toutes les notes pertinentes dans `obsidian-docs/` pour que l’IA puisse les lire facilement.

---

## 📄 Documentation Obsidian intégrée

Le dossier `obsidian-docs/` contient :  
- **00-introduction.md** : contexte du projet et objectifs du MVP  
- **01-schema-donnees.md** : modèles métier et relations  
- **02-architecture-technique.md** : choix techniques et stack  
- **03-validation-erreurs.md** : règles de validation et gestion des erreurs  

Ces notes servent à **fournir un contexte complet au modèle IA**, garantissant que le code généré respecte les décisions de conception et les contraintes métier.

---

## ✅ Bonnes pratiques

- Commits fréquents et explicites  
- Tests unitaires et fonctionnels pour chaque fonctionnalité  
- Documentation continue dans `obsidian-docs/`  
- Maintien d’une TODO list pour le MVP  
- Données de test pour valider rapidement les fonctionnalités  

---

## ⚖️ Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
