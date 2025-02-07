
# import os
# import streamlit as st
# import json
# import google.generativeai as genai
# from PyPDF2 import PdfReader
# from PIL import Image

# # Charger la clé API Google
# api_key = os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=api_key)

# st.title("📄 Extraction Automatique d'Informations")

# # Étape 1 : Upload du fichier (PDF ou Image)
# uploaded_file = st.file_uploader("📥 Téléchargez un PDF ou une Image", type=["pdf", "png", "jpg", "jpeg"])

# # Liste des champs possibles pour extraction
# possible_fields = [
#     "documentType", "number", "nationality", "firstName", "lastName",
#     "dateOfBirth", "sex", "height", "placeOfBirth", "issueDate",
#     "expiryDate", "placeOfIssue"
# ]

# # Sélection des champs par l'utilisateur
# selected_fields = st.multiselect(
#     "Sélectionnez les informations à extraire :",
#     options=possible_fields,
#     default=possible_fields
# )

# # Fonction pour extraire le texte d'un PDF
# def get_pdf_text(pdf_docs):
#     """Extrait le texte d'un PDF"""
#     text = ""
#     for pdf in pdf_docs:
#         pdf_reader = PdfReader(pdf)
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#     return text

# # Fonction pour envoyer une image à Gemini et récupérer l'extraction
# def extract_info_from_image(uploaded_file, selected_fields):
#     """Envoie l'image à Gemini et retourne les informations extraites"""
#     # Génération dynamique du prompt basé sur les champs sélectionnés
#     selected_fields_str = ", ".join(selected_fields)
#     prompt = f"""
#     Analyse ce document et extrais uniquement les informations suivantes : {selected_fields_str}.
#     Retourne les résultats sous forme de texte brut avec une structure clé:valeur
#     """

#     # Convertir l'image téléchargée en format PIL
#     image = Image.open(uploaded_file)

#     # Envoyer l'image et le prompt à Gemini
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content([prompt, image])

#     # Retourner le texte brut extrait par Gemini
#     return response.text.strip()

# # Fonction pour gérer l'upload PDF et la recherche RAG
# def process_pdf(uploaded_file, selected_fields):
#     """Traite le PDF et effectue la recherche RAG"""
#     # Extraire le texte du PDF
#     pdf_text = get_pdf_text([uploaded_file])

#     # Découper le texte en chunks pour le traitement
#     text_chunks = get_text_chunks(pdf_text)

#     # Convertir les chunks en vector store
#     vector_store = get_vector_store(text_chunks)

#     # Rechercher les informations dans le vector store
#     result = vector_store.similarity_search(" ".join(selected_fields))

#     # Retourner les résultats sous forme de texte
#     return result

# # Logique de traitement selon le type de fichier téléchargé
# if uploaded_file:
#     st.image(uploaded_file, caption="Image téléchargée", use_container_width=True)

#     # Vérification du type de fichier (PDF ou Image)
#     if uploaded_file.type == "application/pdf":
#         # Traitement du PDF
#         if st.button("Extraire les données du PDF"):
#             result = process_pdf(uploaded_file, selected_fields)
#             st.subheader("Résultats de l'extraction (RAG PDF) :")
#             st.write(result)
    
#     else:
#         # Traitement de l'image
#         if st.button("Extraire les données de l'image"):
#             extracted_info = extract_info_from_image(uploaded_file, selected_fields)
#             st.subheader("Résultats de l'extraction de l'image :")
#             st.text(extracted_info)

#             # Exporter le résultat en format JSON
#             output_json = {field: extracted_info for field in selected_fields}
#             json_filename = "extracted_info.json"
            
#             # Sauvegarder et permettre le téléchargement
#             with open(json_filename, "w", encoding="utf-8") as json_file:
#                 json.dump(output_json, json_file, ensure_ascii=False, indent=4)
            
#             # Télécharger le fichier JSON
#             with open(json_filename, "rb") as json_file:
#                 st.download_button(
#                     label="Télécharger le fichier JSON",
#                     data=json_file,
#                     file_name=json_filename,
#                     mime="application/json"
#                 )



# import streamlit as st
# import time
# import logging
# import json
# import pandas as pd
# from pathlib import Path
# from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
# from docling.datamodel.base_models import InputFormat
# from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption
# from docling.pipeline.simple_pipeline import SimplePipeline
# from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# import google.generativeai as genai
# from langchain_community.vectorstores import FAISS
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.chains.question_answering import load_qa_chain
# from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv
# import os

# ################################################################
# import streamlit as st
# import google.generativeai as genai
# import json
# import os
# from PIL import Image
# from dotenv import load_dotenv
# from pathlib import Path
# import os
# import json
# from dotenv import load_dotenv
# import streamlit as st
# from PIL import Image

# # Charger les variables d'environnement
# load_dotenv()
# api_key = os.getenv("GOOGLE_API_KEY")

# if not api_key:
#     st.error("La clé API Google n'a pas été trouvée dans le fichier .env.")
#     st.stop()

# genai.configure(api_key=api_key)

# st.title("Extraction et Exportation de données d'un document")

# # Étape 1 : Upload du fichier
# uploaded_file = st.file_uploader("Téléchargez une image ou un document", type=["jpg", "jpeg", "png", "pdf", "docx"])

# # Liste des champs disponibles pour extraction
# possible_fields = [
#     "documentType", "number", "nationality", "firstName", "lastName",
#     "dateOfBirth", "sex", "height", "placeOfBirth", "issueDate",
#     "expiryDate", "placeOfIssue"
# ]

# if uploaded_file:
#     st.image(uploaded_file, caption="Image téléchargée", use_container_width=True)

#     # Étape 2 : Sélection des champs à extraire
#     selected_fields = st.multiselect(
#         "Sélectionnez les informations à extraire :",
#         options=possible_fields,
#         default=possible_fields  # Tout sélectionner par défaut
#     )

#     # Bouton pour lancer l'extraction
#     if st.button("Extraire les données"):
#         model = genai.GenerativeModel("gemini-1.5-flash")

#         # Génération dynamique du prompt en fonction des champs choisis
#         selected_fields_str = ", ".join(selected_fields)
#         prompt = f"""
#         Analyse ce document et extrais uniquement les informations suivantes : {selected_fields_str}.
#         """

#         # Convertir le fichier uploadé en image pour l'envoyer à Gemini
#         image = Image.open(uploaded_file)

#         # Générer le contenu via le modèle avec l'image et le prompt
#         response = model.generate_content([prompt, image])

#         st.subheader("Résultat de l'extraction")

#         # Affichage de la réponse brute pour mieux comprendre
#         st.write("Réponse brute de Gemini :")
#         output= response.text
#         st.write(output)
