import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv   
import os
import json
import pandas as pd
import streamlit as st
from PIL import Image
load_dotenv()
import google.generativeai as genai

def get_pdf_text(pdf_docs):
    """Extrait le texte d'un PDF"""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    """Divise le texte en morceaux pour la vectorisation"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    """Vectorise les morceaux de texte avec FAISS"""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store

def get_selected_infos():
    """Génère un prompt basé sur les infos sélectionnées"""

 
    prompt_template = """     
    Extraire les informations  de la manière la plus détaillée possible à partir du document PDF fourni et des elements selectionnés par l'utilisateur. 
    Assurez-vous de fournir la reponse sous forme de texte brute et separe les en clé valeur. Si la réponse ne peut pas être déterminée à partir du document PDF,  
    "Marque seulement non trouvé", sans fournir de réponse incorrecte.

    Document PDF fourni : {context}
    \n
    Question : \n{selected_fields}\n

     Réponse :
    
    """

    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)
    prompt = PromptTemplate(template = prompt_template, input_variables = ["context","selected_fields"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain


def user_input(selectedd_fields):
    

    """Extrait les infos sélectionnées directement depuis le texte"""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(selectedd_fields)

    # Recherche des infos sélectionnées
    selected_chain = get_selected_infos()
    response = selected_chain.invoke({"input_documents": docs, "selected_fields": selectedd_fields})
    output_text = response.get("output_text", "").strip()
    formatted_text = "\n".join([f"{line}" for line in output_text.split("\n")])
    st.subheader("🔍 Résultat brut de l'extraction")
    st.text(formatted_text)
    # Transformation en JSON
    output_json = {}
    output_text = response.get("output_text", "").strip()  # Récupération sûre du texte

    for line in output_text.split("\n"):
        if ":" in line:  # Vérifier si la ligne contient une clé et une valeur
            key, value = line.split(":", 1)  # Séparer la clé de la valeur
            output_json[key.strip()] = value.strip()  # Nettoyage des espaces

     # Retourner l'objet JSON
    return output_json


possible_fields = {
    "Resume": [
        "ÉDUCATION (diplômes, établissements, années)",
        "EXPÉRIENCES (postes, entreprises, dates, descriptions)",
        "COMPÉTENCES (techniques, soft skills)",
        "LANGUES (langues parlées, niveaux)",
        "CERTIFICATIONS (certifications obtenues)",
        "CONTACT (email, téléphone, LinkedIn, etc.)"
    ],
    "Drive-Licence": [
        "documentType",
        "number",
        "nationality",
        "firstName",
        "lastName",
        "dateOfBirth",
        "sex",
        "height",
        "placeOfBirth",
        "issueDate",
        "expiryDate",
        "placeOfIssue"
    ],
    "ID-Card": [
        "documentType",
        "number",
        "nationality",
        "firstName",
        "lastName",
        "dateOfBirth",
        "sex",
        "height",
        "placeOfBirth",
        "issueDate",
        "expiryDate",
        "placeOfIssue"
    ],
    "Invoice": [
        "en_tete (titre, entreprise, date, client, semaine, opération, produit, site)",
        "tableau (numero, identifiant, description, valeur, observation)",
        "total",
        "pied_de_page (entreprises, magasinier (nom, date), autres_signataires (nom, rôle))"
    ],
    "check-point": {
        "Employé": [
            "Nom", 
            "Prénom",
            "Client",
            "Site",
            "Période"
        ],
        "Horaires": {
            "S1": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"],
            "S2": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"],
            "S3": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"],
            "S4": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        }
    }
}

def get_selected_check_point_fields(possible_fields):
            selected_fields = {}
            
            # Sélection des champs Employé
            selected_employe_fields = st.multiselect(
                "Sélectionnez les champs Employé :",
                options=possible_fields["check-point"]["Employé"],
                default=possible_fields["check-point"]["Employé"]
            )
            if selected_employe_fields:
                selected_fields["Employé"] = selected_employe_fields

            # Sélection des semaines
            selected_shifts = st.multiselect(
                "Sélectionnez les semaines :",
                options=list(possible_fields["check-point"]["Horaires"].keys()),
                default=list(possible_fields["check-point"]["Horaires"].keys())
            )

            horaires_selection = {}
            for shift in selected_shifts:
                selected_days = st.multiselect(
                    f"Sélectionnez les jours pour {shift} :",
                    options=possible_fields["check-point"]["Horaires"][shift],
                    default=possible_fields["check-point"]["Horaires"][shift]
                )

                day_selection = {}
                for day in selected_days:
                    selected_hours = st.multiselect(
                        f"Sélectionnez les horaires pour {day} ({shift}) :",
                        options=["Arrivée", "Départ"],
                        default=["Arrivée", "Départ"]
                    )
                    if selected_hours:
                        day_selection[day] = selected_hours

                if day_selection:
                    horaires_selection[shift] = day_selection

            if horaires_selection:
                selected_fields["Horaires"] = horaires_selection
            
            return selected_fields
        


selected_fields_str= get_selected_check_point_fields(possible_fields)

def extract_info_from_image(uploaded_file, selected_fields_str):
    """Envoie l'image à Gemini et retourne les informations extraites"""
    # Génération dynamique du prompt basé sur les champs sélectionnés
    
    prompt = f"""
    Analyse ce document et extraits uniquement les informations suivantes : {selected_fields_str}.
    
    Retourne un **JSON valide**, strictement conforme au format suivant je rappelle que ce format est juste un exemple tu dois juste te baser sur ça pour repondre :

    ```json
    {{
      "Employé": ["Nom"],
      "Horaires": {{
        "S": {{
          "Lundi": ["Arrivée", "Départ"]
        }}
      }}
    }}
    ```
    **Rappel :**

    **ATTENTION :**  
    - Ne retourne que du JSON pur, sans texte supplémentaire.
    - Assure-toi que les clés et valeurs soient bien formatées.
    """


    # Convertir l'image téléchargée en format PIL
    image = Image.open(uploaded_file)

    # Envoyer l'image et le prompt à Gemini
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([prompt, image])
    output_text = response.text.strip()
    st.subheader("Résultat brut de l'extraction")
    st.write(output_text)

    # 🔹 Extraction stricte du JSON dans le texte renvoyé
    try:
        if "```json" in output_text:
            output_text = output_text.split("```json")[1].split("```")[0].strip()

        output_json = json.loads(output_text)
        
        return output_json
    except json.JSONDecodeError:
        st.error("❌ Le modèle n'a pas retourné un JSON valide. Vérifie le format renvoyé.")
        return {}



def save_and_download_json(data):
    """Sauvegarde les données JSON et propose le téléchargement"""
    json_filename = "extracted.json"
    
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    st.subheader("📥 Télécharger le fichier JSON :")
    with open(json_filename, "rb") as file:
        st.download_button("⬇️ Télécharger", file, file_name=json_filename, mime="application/json")