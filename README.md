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

# #Architecture du Processus - SNL

## Déroulement du processus

```snl
ALGORITHM Kaadoc_Document_Processing;
VAR
    InputFile, ProcessedText, SelectedParts, ConvertedOutput : TEXT;
    FaissIndex : INDEX;
    ExtractionResults, GeminiResults : STRUCT;
BEGIN
    // Étape 0 : Initialisation de l'environnement
    CALL InitializeModules();
    CALL LoadConfigurations("config/settings.py");
    CALL LoadEnvironmentVariables("config/.env");
    
    // Étape 1 : Chargement du document (PDF ou Image)
    InputFile := CALL UploadFile();   // Par exemple via l'interface Streamlit
    
    // Étape 2 : Extraction du texte structuré avec Docling
    ExtractionResults := CALL Docling.Extract(InputFile);
        // Docling extrait le texte, la mise en page, et segmente le document.
    
    // Étape 3 : Indexation des parties extraites avec Faiss
    FaissIndex := CALL Faiss.BuildIndex(ExtractionResults);
        // Faiss indexe le contenu pour permettre une recherche par similarité.
    
    // Étape 4 : Analyse du document par Gemini via LangChain
    GeminiResults := CALL Gemini.Analyze(FaissIndex, Query = "Identifier les sections à convertir");
        // Gemini détermine quelles parties du document sont pertinentes pour la conversion.
    
    // Étape 5 : Sélection des parties à convertir
    SelectedParts := CALL SelectRelevantParts(GeminiResults);
        // On sélectionne les parties identifiées par Gemini.
    
    // Étape 6 : Conversion des parties sélectionnées en code ou format structuré (JSON/CSV)
    ConvertedOutput := CALL Gemini.Convert(SelectedParts, TargetFormat = "JSON");
        // Gemini, via LangChain, génère la conversion en utilisant ses capacités LLM.
    
    // Étape 7 : Exportation du résultat final
    CALL ExportOutput(ConvertedOutput, Destination = "data/output/");
    
    // Fin du processus
    OUTPUT ConvertedOutput;
END.

---------------------------------------------------------------------------------------
MODULE InitializeModules;
BEGIN
    // Importer les modules essentiels
    ConversionModule := MODULE("Kaadoc.backend.convert");      // Conversion des données (convert.py)
    ExtractionModule := MODULE("Kaadoc.backend.process");        // Extraction du texte (process.py)
    ExportModule := MODULE("Kaadoc.backend.export");             // Export des données (export.py)
    DatabaseModule := MODULE("Kaadoc.database.db_connector");    // Connexion BDD (db_connector.py)
    DoclingModule := MODULE("Docling.Core");                     // Bibliothèque Docling pour l'extraction avancée
    GeminiModule := MODULE("LangChain.Gemini");                  // Module Gemini via LangChain
    FaissModule := MODULE("Faiss.Indexer");                      // Module Faiss pour l'indexation
END.


---------------------------------------------------------------
**Étape 1 : Télécharger le fichier via l'interface utilisateur**
MODULE UploadFile;
VAR
    FilePath : STRING;
BEGIN
    // Permet à l'utilisateur de télécharger un fichier via l'interface Streamlit
    CALL StreamlitInterface.UploadFile(FilePath);  // Fichier : Kaadoc/frontend/main.py
    RETURN FilePath;
END.


---------------------------------------------------------
**Étape 2 : Extraire le texte du fichier via le module d'extraction**
MODULE Docling.Extract;
VAR
    InputFile : FILE;
    ExtractionResults : STRUCT;
BEGIN
    // Utilisation de Docling pour extraire le texte et la structure du document
    CALL DoclingModule.ExtractDocument(InputFile, ExtractionResults);
    RETURN ExtractionResults;
END.


------------------------------------------------------------------------------------------------
**Étape 3 : Créér une base de données vectorielles à partir des données extraites avec Faiss**
MODULE Faiss.BuildIndex;
VAR
    ExtractionResults : STRUCT;
    Index : INDEX;
BEGIN
    // Construction d'un index Faiss à partir des résultats d'extraction
    CALL FaissModule.CreateIndex(ExtractionResults, Index);
    RETURN Index;
END.


--------------------------------------------------------------------------------------------
**Étape 4 : Analyser le document avec Gemini pour une conversion specifique ou totale**
MODULE Gemini.Analyze;
VAR
    FaissIndex : INDEX;
    Query : TEXT;
    AnalysisResults : STRUCT;
    SelectedParts : TEXT;
    GeminiResults : STRUCT;
BEGIN
    // Utilisation de Gemini via LangChain pour analyser l'index et identifier les sections pertinentes
    CALL GeminiModule.AnalyzeIndex(FaissIndex, Query, AnalysisResults);
    // Sélection des parties pertinentes à convertir basées sur l'analyse de Gemini
    CALL DataSelector.Filter(GeminiResults, Criteria = "conversion_relevance", SelectedParts);
    RETURN AnalysisResults;SelectedParts;
END.

--------------------------------------------------------------
**Étape 5 : Convertir les données extraites en format JSON ou CSV**
MODULE Gemini.Convert;
VAR
    SelectedParts : TEXT;
    ConvertedOutput : TEXT;
BEGIN
    // Conversion des parties sélectionnées en format JSON ou CSV via Gemini
    CALL GeminiModule.ConvertToFormat(SelectedParts, TargetFormat = "JSON", ConvertedOutput);
    RETURN ConvertedOutput;
END.


--------------------------------------------------------------
**Étape 6 : Exporter les données dans une base de données ou fichier**
MODULE ExportData;
VAR
    OutputFile : FILE;
BEGIN
    // Option 1 : Exporter vers un fichier local
    CALL FileExporter.SaveToFile(OutputFile, "Kaadoc/data/output/"); // Fichier : `Kaadoc/backend/export.py`
    
    // Option 2 : Exporter vers une base de données externe
    CALL DatabaseModule.SaveDataToDatabase(OutputFile); // Fichier : `Kaadoc/database/db_connector.py`
END.


------------------------------------------------------------------
**Étape 7 : Optionnel : Sauvegarder les données dans une base de données externe**
MODULE SaveDataToDatabase;
VAR
    StructuredData : TEXT;
BEGIN
    // Sauvegarde des données dans une base de données externe
    IF DatabaseConnection IS PostgreSQL THEN
        CALL PostgreSQL.SaveData(StructuredData, "table_name");  // Fichier : `Kaadoc/database/db_connector.py`
    ELSE IF DatabaseConnection IS MongoDB THEN
        CALL MongoDB.SaveData(StructuredData, "collection_name");  // Fichier : `Kaadoc/database/db_connector.py`
    ENDIF;
END.


---


Explication du Processus

-Initialisation

Tous les modules nécessaires sont importés et initialisés, y compris Docling pour l'extraction, Gemini via LangChain pour l'analyse/conversion, et Faiss pour l'indexation.

-Téléchargement
L'utilisateur télécharge un document (PDF, image, etc.) via l'interface Streamlit.

-Extraction
Docling extrait le contenu du document, y compris la structure (texte, tableaux, etc.).

-Indexation
Faiss est utilisé pour construire un index à partir des données extraites, facilitant la recherche par similarité.

-Analyse par Gemini
Gemini examine l'index pour identifier les sections pertinentes qui doivent être converties, selon une requête prédéfinie.

-Sélection
Les parties identifiées par l'utilisateur sont sélectionnées et filtrées pour la conversion.

-Conversion
Gemini convertit ces sections sélectionnées en un format structuré (par exemple, JSON).

-Exportation
Le résultat final est exporté dans le dossier de sortie ou vers une base de données externe.


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

**2. Installer les dépendances** :

   ```bash
   pip install -r requirements.txt
   ```

 **3. Lancer l'application Streamlit** :

   ```bash
   streamlit run main.py
   ```
