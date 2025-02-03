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



# Architecture SNL de KaadocV1 - Extraction et Structuration de Données

## Algorithme principal : `KaadocV1_Extraction_and_Structuration`

### Variables
- `InputFile` : Fichier à traiter
- `ProcessedText` : Texte extrait du fichier
- `StructuredData` : Données extraites et structurées
- `DatabaseConnection` : Connexion à la base de données
- `OutputFile` : Fichier de sortie (JSON, CSV)
- `ConversionModule`, `ExtractionModule`, `ExportModule`, `DatabaseModule` : Modules utilisés dans le processus

### Déroulement du processus

```snl
BEGIN
    // Initialiser les modules nécessaires
    CALL InitializeModules();

    // Étape 1 : Télécharger le fichier via l'interface utilisateur
    CALL UploadFile(InputFile);
    
    // Étape 2 : Extraire le texte du fichier via le module d'extraction
    CALL ExtractionModule.ExtractText(InputFile, ProcessedText);

    // Étape 3 : Sélectionner les informations spécifiques dans le texte extrait
    CALL ExtractionModule.SelectData(ProcessedText, StructuredData);
    
    // Étape 4 : Convertir les données extraites en format JSON ou CSV
    CALL ConversionModule.ConvertToJsonOrCsv(StructuredData, OutputFile);

    // Étape 5 : Exporter les données dans une base de données ou fichier
    CALL ExportModule.ExportData(OutputFile);
    
    // Étape 6 : Optionnel : Sauvegarder les données dans une base de données externe
    CALL DatabaseModule.SaveDataToDatabase(StructuredData);
END.


MODULE InitializeModules;
BEGIN
    // Initialisation des modules backend
    ConversionModule := MODULE("Kaadoc.backend.convert");
    ExtractionModule := MODULE("Kaadoc.backend.process");
    ExportModule := MODULE("Kaadoc.backend.export");
    DatabaseModule := MODULE("Kaadoc.database.db_connector");
    
    // Chargement des configurations
    CALL LoadConfigurations("config/settings.py");
    CALL LoadEnvironmentVariables(".env");
END.


---------------------------------------------------------------

MODULE UploadFile;
VAR
    FilePath : STRING;
BEGIN
    // L'interface utilisateur permet à l'utilisateur de télécharger le fichier
    CALL StreamlitInterface.UploadFile(FilePath);
    RETURN FilePath;
END.

---------------------------------------------------------

MODULE ExtractText;
VAR
    InputFile : FILE;
    ExtractedText : TEXT;
BEGIN
    // Si le fichier est un PDF
    IF FileType(InputFile) == "PDF" THEN
        CALL TesseractOCR.ExtractFromPDF(InputFile, ExtractedText);
    ENDIF;
    
    // Si le fichier est une image
    IF FileType(InputFile) == "Image" THEN
        CALL TesseractOCR.ExtractFromImage(InputFile, ExtractedText);
    ENDIF;

    RETURN ExtractedText;
END.
------------------------------------------

MODULE SelectData;
VAR
    ExtractedText : TEXT;
    SelectedData : TEXT;
BEGIN
    // Logique de sélection des informations pertinentes
    CALL DataSelector.SelectFields(ExtractedText, SelectedData, Fields = ["CNI", "Factures", "CV"]);
    RETURN SelectedData;
END.

--------------------------------

MODULE ConvertToJsonOrCsv;
VAR
    StructuredData : TEXT;
    OutputFile : FILE;
BEGIN
    // Conversion des données en JSON ou CSV
    CALL LlamaIndex.ConvertData(StructuredData, Format = "JSON", OutputFile);
    RETURN OutputFile;
END.

------------------------
MODULE ExportData;
VAR
    OutputFile : FILE;
BEGIN
    // Option 1 : Exporter vers un fichier local
    CALL FileExporter.SaveToFile(OutputFile, "data/output/");
    
    // Option 2 : Exporter vers une base de données externe
    CALL DatabaseModule.SaveDataToDatabase(OutputFile);
END.


-------------------------------

MODULE SaveDataToDatabase;
VAR
    StructuredData : TEXT;
BEGIN
    // Sauvegarde des données dans une base de données externe
    IF DatabaseConnection IS PostgreSQL THEN
        CALL PostgreSQL.SaveData(StructuredData, "table_name");
    ELSE IF DatabaseConnection IS MongoDB THEN
        CALL MongoDB.SaveData(StructuredData, "collection_name");
    ENDIF;
END.




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