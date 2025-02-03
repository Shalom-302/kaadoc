# 📌 KaadocV1 - Extraction et Structuration de Données

## 📖 Description du Projet
**Kaadoc** est une application d'intelligence artificielle générative permettant de convertir des données non structurées (PDF, images, textes, sons, vidéos) en données structurées au format **CSV** ou **JSON**. L'application permet ensuite de **télécharger** les données converties ou de les **intégrer** directement dans une base de données externe.

L'interface est développée avec **Streamlit**, permettant une UX fluide et intuitive. Le backend repose sur **Langchain** et **LlamaIndex** pour l'extraction et la conversion des données.

---

## 🎯 Fonctionnalités Principales

✅ **Upload de fichiers** : Supporte **PDF, images, textes, sons, vidéos**.
✅ **Extraction des données** : Convertit les documents non structurés en texte exploitable.
✅ **Sélection des informations** : Possibilité d'extraire toutes les informations ou de sélectionner des champs spécifiques des (CNI, Factures, CV, etc.).
✅ **Conversion JSON/CSV** : Transformation des données extraites en JSON ou CSV via **LlamaIndex**.
✅ **Export des données** : Téléchargement des fichiers convertis ou intégration à une **base de données externe**.

---

## 🏗 Architecture du Projet

### 📂 **Structure des fichiers**

```
Kaadoc/
│-- backend/              # Gestion de l'extraction, conversion et export
│   │-- __init__.py       # Initialisation du module backend
│   │-- process.py        # Extraction de texte depuis les fichiers uploadés
│   │-- schema.py         # Définition des schémas de structuration des données
│   │-- convert.py        # Transformation en JSON/CSV
│   │-- export.py         # Gestion de l'exportation (téléchargement & BDD)
│   │-- utils.py          # Fonctions utilitaires (nettoyage, logs, erreurs)
│
│-- frontend/             # Interface utilisateur avec Streamlit
│   │-- __init__.py
│   │-- main.py            # Application principale avec Streamlit
│   │-- components.py     # Composants réutilisables pour l'UI
│
│-- data/                 # Dossier contenant les fichiers uploadés et les sorties
│   │-- input/            # Fichiers uploadés
│   │-- output/           # Fichiers convertis (JSON, CSV)
│
│-- config/               # Configuration globale du projet
│   │-- settings.py       # Variables de configuration
│   │-- .env              # Stockage des clés API et configurations sensibles
│
│-- database/             # Intégration avec une base de données externe
│   │-- db_connector.py   # Connexion à PostgreSQL/MongoDB
│   │-- models.py         # Définition des modèles de données
│
│-- tests/                # Tests unitaires et d'intégration
│   │-- test_process.py   # Test de l'extraction
│   │-- test_convert.py   # Test de la conversion
│   │-- test_export.py    # Test de l'export
│
│-- requirements.txt      # Liste des dépendances
│-- README.md             # Documentation du projet
```

---

## 🔥 Technologies Utilisées

- **Langchain** : Extraction et structuration des données
- **LlamaIndex** : Conversion JSON/CSV
- **Streamlit** : Interface utilisateur
- **Tesseract OCR** : Extraction de texte depuis les images
- **PostgreSQL / MongoDB** : Stockage des données extraites
- **Pandas** : Manipulation des données structurées (CSV)

---

## 🚀 Installation & Utilisation

1. **Cloner le dépôt** :
   ```bash
   git clone https://gitlab.kaanari.com/training1/kaadoc-rag.git
   cd <repo-folder>
   ```
2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```
3. **Lancer l'application Streamlit** :
   ```bash
   streamlit run main.py
   ```

## 📌 Prochaines améliorations

- Ajouter la prise en charge d'autres types de fichiers.
- Intégration avec des **API externes** pour stockage et récupération automatique des données.

---

📩 **Contact & Contributions**
Les contributions sont les bienvenues ! Pour toute suggestion ou amélioration, n'hésitez pas à ouvrir une issue ou un pull request. 🚀

---