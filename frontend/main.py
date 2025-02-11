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
import streamlit as st
from PIL import Image
load_dotenv()
import google.generativeai as genai


# Connexion à Redis


apikey = os.getenv("GOOGLE_API_KEY")
if not apikey:
    st.error("La clé API Google n'a pas été trouvée dans le fichier .env.")
    st.stop()

genai.configure(api_key=apikey)


possible_fields = [
    "documentType", "number", "nationality", "firstName", "lastName",
    "dateOfBirth", "sex", "height", "placeOfBirth", "issueDate",
    "expiryDate", "placeOfIssue"
]

selected_fields = st.multiselect(
    "Sélectionnez les informations à extraire :",
    options=possible_fields,
    default=possible_fields)

selectedd_fields = ", ".join(selected_fields)


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





def extract_info_from_image(uploaded_file, selected_fields):
    """Envoie l'image à Gemini et retourne les informations extraites"""
    # Génération dynamique du prompt basé sur les champs sélectionnés
    selected_fields_str = ", ".join(selected_fields)
    prompt = f"""
    Analyse ce document et extrais uniquement les informations suivantes : {selected_fields_str}.
    Retourne les résultats sous forme de texte brut avec une structure clé:valeur
    """

    # Convertir l'image téléchargée en format PIL
    image = Image.open(uploaded_file)

    # Envoyer l'image et le prompt à Gemini
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([prompt, image])
    output_text = response.text.strip()
    st.subheader("Résultat brut de l'extraction")
    st.text(output_text)
    # Retourner le texte brut extrait par Gemini
            # 🔹 **Transformation en JSON**
    output_json = {}
    for line in output_text.split("\n"):
        if ":" in line:  # Vérifier si la ligne contient une clé et une valeur
                key, value = line.split(":", 1)  # Séparer la clé de la valeur
                output_json[key.strip()] = value.strip()  # Nettoyage des espaces
                
    return output_json



def save_and_download_json(data):
    """Sauvegarde les données JSON et propose le téléchargement"""
    json_filename = "extracted.json"
    
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    st.subheader("📥 Télécharger le fichier JSON :")
    with open(json_filename, "rb") as file:
        st.download_button("⬇️ Télécharger", file, file_name=json_filename, mime="application/json")



st.title("📄 Extraction Automatique d'Informations")
uploaded_file = st.file_uploader("📥 Téléchargez un PDF ou une Image", type=["pdf", "png", "jpg", "jpeg"])

# Liste des champs possibles pour extraction
# Sélection des champs par l'utilisateur

if uploaded_file:
    file_type = uploaded_file.type
    
    if "pdf" in file_type:
        st.write("pdf file uploaded")
        if st.button("Process", type="primary"):
            
            with st.spinner("📄 Traitement du PDF en cours..."):
        
            # Extraction du texte
                extracted_text = get_pdf_text([uploaded_file])

                # Découpage en chunks + vectorisation
                text_chunks = get_text_chunks(extracted_text)
                get_vector_store(text_chunks)
                st.success("pdf chunked successfully")
        # Extraction automatique des infos
            if selectedd_fields:
                """Infos sélectionnées directement depuis le texte"""
                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
                docs = new_db.similarity_search(selectedd_fields)

                extracted_data = user_input(selectedd_fields)
                st.subheader("Résultat des données en json")
                st.json(extracted_data)
                save_and_download_json(extracted_data)
      
            

    elif "image" in file_type:
        st.image(uploaded_file, caption="Image téléchargée", use_container_width=True)
        if st.button("Process", type="primary"):
            st.subheader("🖼️ Traitement de l'Image en cours...")
            # Envoi à Gemini pour traitement
            # Extraction automatique des infos
            extracted_data = extract_info_from_image(uploaded_file,selected_fields)
        
            st.subheader("resultat des données en json")
            # Affichage et téléchargement
            st.json(extracted_data)
            save_and_download_json(extracted_data)




