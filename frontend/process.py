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

All_json = {}


possible_fields = {
    "All_json":{
            
        },
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
    "Work-Schedule": [
        "AllName",  # Nom complet détecté
        "schedule",  # Un dictionnaire des jours et horaires
        "totals"  # Totaux des présences
    ],
     "Work-Schedule-1": [
        "nom et prenom",
        "client",
        "week_start",
        "week_end",
        "week_label",
        "product",
        "task",
        "site",
        "schedule_vendredi_date",
        "schedule_vendredi_day",
        "schedule_vendredi_night",
        "schedule_samedi_date",
        "schedule_samedi_day",
        "schedule_samedi_night",
        "schedule_dimanche_date",
        "schedule_dimanche_day",
        "schedule_dimanche_night",
        "schedule_lundi_date",
        "schedule_lundi_day",
        "schedule_lundi_night",
        "schedule_mardi_date",
        "schedule_mardi_day",
        "schedule_mardi_night",
        "schedule_mercredi_date",
        "schedule_mercredi_day",
        "schedule_mercredi_night",
        "schedule_jeudi_date",
        "schedule_jeudi_day",
        "schedule_jeudi_night",
        "total_day",
        "total_night",
        "total_hours",
        "signature_exceliam_responsable",
        "signature_sea_invest_responsable",
        "signature_magasinier",
        "signature_magasinier_date"
    ],
     
      "Work-Schedule-2": {
        "client": "",
        "week_start": "",
        "week_end": "",
        "week_label": "",
        "product": "",
        "task": "",
        "site": "",
        "schedule": {
            "vendredi": {"date": "", "day": "", "night": ""},
            "samedi": {"date": "", "day": "", "night": ""},
            "dimanche": {"date": "", "day": "", "night": ""},
            "lundi": {"date": "", "day": "", "night": ""},
            "mardi": {"date": "", "day": "", "night": ""},
            "mercredi": {"date": "", "day": "", "night": ""},
            "jeudi": {"date": "", "day": "", "night": ""}
        },
        "totals": {
            "total_day": "",
            "total_night": "",
            "total_hours": ""
        },
        "signatures": {
            "exceliam_responsable": "",
            "sea_invest_responsable": "",
            "magasinier_signature": "",
            "magasinier_date": ""
        }
    },
     
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
        },
        "emargement":[],
        "observation":[]
        
        
    },
    "check-point-1": {
        "Employé": [
            "Nom", 
            "Prénom",
            "Client",
            "Site",
            "Période"
        ],
        "weeks": {
            "S1": {
                "L-25": {"arrivée": "", "pause": "", "reprise": "", "depart": "", "emargement": "", "observation": ""},
                "M-26": {"arrivée": "", "pause": "", "reprise": "", "depart": "", "emargement": "", "observation": ""},
                "M-27": {"arrivée": "", "pause": "", "reprise": "", "depart": "", "emargement": "", "observation": ""},
                "J-28": {"arrivée": "", "pause": "", "reprise": "", "depart": "", "emargement": "", "observation": ""},
                "V-29": {"arrivée": "", "pause": "", "reprise": "", "depart": "", "emargement": "", "observation": ""},
                "S-30": {"arrivée": "", "pause": "", "reprise": "", "depart": "", "emargement": "", "observation": ""}
            },
            "S2": {
                "L-02": {"arrivée": "", "pause": "", "reprise": "", "departure": "", "emargement": "", "observation": ""},
                "M-03": {"arrivée": "", "pause": "", "reprise": "", "departure": "", "emargement": "", "observation": ""},
                "M-04": {"arrivée": "", "pause": "", "reprise": "", "departure": "", "emargement": "", "observation": ""},
                "J-05": {"arrivée": "", "pause": "", "reprise": "", "departure": "", "emargement": "", "observation": ""},
                "V-06": {"arrivée": "", "pause": "", "reprise": "", "departure": "", "emargement": "", "observation": ""}
            },
            "S3": {
                "S-07": {"arrivée": "", "pause": "", "reprise": "", "departure": "", "emargement": "", "observation": ""},
                "D-08": {"arrivée": "", "pause": "", "reprise": "", "departure": "", "emargement": "", "observation": ""},
                "L-09": {"arrivée": "", "pause": "", "reprise": "", "departure": "", "emargement": "", "observation": ""}
            }
        },
        "signatures": {
            "supervisor": "",
            "service_manager": "",
            "hr_supervisor": "",
            "hr_coordinator": ""
        },
        
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
                        options=["Arrivée", "Départ","pause","reprise","emargement","observation"],
                        default=["Arrivée", "Départ","pause","reprise","emargement","observation"]
                    )
                    if selected_hours:
                        day_selection[day] = selected_hours

                if day_selection:
                    horaires_selection[shift] = day_selection

            if horaires_selection:
                selected_fields["Horaires"] = horaires_selection
            
            return selected_fields
        


selected_fields_str= get_selected_check_point_fields(possible_fields)


# def get_selected_check_points_1(possible_fields):
#             selected_fields = {}
            
#             # Sélection des champs Employé
#             selected_employe_fields = st.multiselect(
#                 "Sélectionnez les champs Employé :",
#                 options=possible_fields["check-point-1"]["Employé"],
#                 default=possible_fields["check-point-1"]["Employé"]
#             )
#             if selected_employe_fields:
#                 selected_fields["Employé"] = selected_employe_fields

#             # Sélection des semaines
#             selected_shifts = st.multiselect(
#                 "Sélectionnez les semaines :",
#                 options=list(possible_fields["check-point-1"]["weeks"].keys()),
#                 default=list(possible_fields["check-point-1"]["weeks"].keys())
#             )

#             horaires_selection = {}
#             for shift in selected_shifts:
#                 selected_days = st.multiselect(
#                     f"Sélectionnez les jours pour {shift} :",
#                     options=possible_fields["check-point-1"]["weeks"][shift],
#                     default=possible_fields["check-point-1"]["weeks"][shift]
#                 )

#                 day_selection = {}
#                 for day in selected_days:
#                     selected_hours = st.multiselect(
#                     f"Sélectionnez les horaires pour {day} ({shift}) :",
#                         options=["arrival", "pause","resume", "departure", "observation"],
    
#                         default=["arrival", "pause","resume", "departure", "observation"]
#                     )
#                     if selected_hours:
#                         day_selection[day] = selected_hours

#                 if day_selection:
#                     horaires_selection[shift] = day_selection

#             if horaires_selection:
#                 selected_fields["weeks"] = horaires_selection
            
#             return selected_fields
    

# check_point_1 = get_selected_check_points_1(possible_fields)


def extract_info_from_image(uploaded_file, selected_fields_str):
    """Envoie l'image à Gemini et retourne les informations extraites"""
    # Génération dynamique du prompt basé sur les champs sélectionnés
    
    prompt = f"""
Analyse ce document et extraits uniquement les informations suivantes : {selected_fields_str}.
Si tous les champs doivent être extraits, structure-les intégralement dans {All_json} en respectant la présentation et l'organisation du document dans l’image.
verifie aussi les emargements et les observations qui sont en signature manuscrites
Instructions :

Génére un JSON strictement valide, fidèle à la structure des données présentes dans l’image.
Ne laisse aucune donnée de côté : tous les employés et toutes les informations doivent être capturés.
Respecte scrupuleusement la hiérarchie et le format des clés et valeurs visibles dans l’image.
Aucun texte en dehors du JSON : ne retourne que le JSON brut.
Si des valeurs sont absentes ou illisibles, conserve la structure avec des valeurs vides ("" ou null).
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