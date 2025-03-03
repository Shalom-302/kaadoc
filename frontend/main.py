import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from PIL import Image
import json
import google.generativeai as genai
from process import (
    possible_fields,

    get_selected_check_point_fields,
    get_selected_timesheet_fields, # Ensure this is also imported if used
    get_pdf_text,
    get_text_chunks,
    get_vector_store,
    extract_info_from_image,
    user_input,
    save_and_download_json
)

# Charger les variables d'environnement
load_dotenv()
apikey = os.getenv("GOOGLE_API_KEY")

if not apikey:
    st.error("La clé API Google n'a pas été trouvée dans le fichier .env.")
    st.stop()

genai.configure(api_key=apikey)

# Interface utilisateur
st.title("📄 Extraction Automatique d'Informations")
uploaded_file = st.file_uploader("📥 Téléchargez un PDF ou une Image", type=["pdf", "png", "jpg", "jpeg"])
document_type = st.selectbox("Sélectionnez un type de document", list(possible_fields.keys()), key="document_type_selectbox") # Added key

selected_fields_str = "" # Initialize here
selected_fields_timesheet_variable = None # Initialize here
selected_fields_checkpoint_variable = None # Initialize here


if document_type:
    st.subheader(f"Champs à extraire pour {document_type}")

    if document_type == "check-point":
        selected_fields_checkpoint_variable = get_selected_check_point_fields(possible_fields)
        selected_fields_str_checkpoint_json = json.dumps(selected_fields_checkpoint_variable, ensure_ascii=False)
        selected_fields_str = selected_fields_str_checkpoint_json

    elif document_type == "Timesheet":
        selected_fields_timesheet_variable = get_selected_timesheet_fields(possible_fields) # Use the variable here
        selected_fields_str_timesheet = json.dumps(selected_fields_timesheet_variable, ensure_ascii=False)
        selected_fields_str = selected_fields_str_timesheet # Assign to the general variable


    elif document_type in possible_fields and document_type not in ["check-point", "Timesheet"] : # Handle other document types
        selected_fields =  st.multiselect(
            "Sélectionnez les informations à extraire :",
            options=possible_fields[document_type],
            default=possible_fields[document_type]
        )
        selected_fields_str = json.dumps(selected_fields) # Convert multiselect to JSON string


    st.write("### Champs sélectionnés :")
    if document_type == "check-point":
        st.json(selected_fields_checkpoint_variable)
    elif document_type == "Timesheet":
         st.json(selected_fields_timesheet_variable)
    elif document_type in possible_fields: # Display for other doc types
        st.json(selected_fields)


# Traitement des fichiers
if uploaded_file and document_type: # Ensure document_type is also selected
    file_type = uploaded_file.type

    if "pdf" in file_type:
        st.success("📄 PDF uploaded successfully")
        if st.button("Convertir en JSON", type="primary", key="pdf_json_button"): # Added key
            with st.spinner("📄 Traitement du PDF..."):
                extracted_text = get_pdf_text([uploaded_file])
                text_chunks = get_text_chunks(extracted_text)
                get_vector_store(text_chunks)

                extracted_data = user_input(", ".join(selected_fields_str)) # Pass selected_fields_str

                st.subheader("Résultat des données en JSON")
                st.json(extracted_data)
                save_and_download_json(extracted_data)

        if st.button("Convertir en CSV", type="primary", key="pdf_csv_button"): # Added key
            with st.spinner("📄 Conversion en CSV..."):
                extracted_data = user_input(selected_fields_str) # Pass selected_fields_str
                df = pd.DataFrame(extracted_data.items(), columns=["Champ", "Valeur"])
                csv_filename = "extracted_data.csv"
                df.to_csv(csv_filename, index=False)

                st.success("✅ CSV exporté avec succès")
                st.download_button("⬇️ Télécharger CSV", open(csv_filename, "rb"), file_name=csv_filename, mime="text/csv", key="pdf_download_button") # Added key

    elif "image" in file_type:
        st.success("🖼 Image uploaded successfully")
        st.image(uploaded_file, caption="Image téléchargée", use_container_width=True)

        if st.button("Convertir en JSON", type="primary", key="image_json_button"): # Added key
            with st.spinner("📄 Traitement de l'image..."):
                # Pass document_type to extract_info_from_image
                extracted_data = extract_info_from_image(uploaded_file, selected_fields_str, document_type)
                st.subheader("Résultat des données en JSON")
                st.json(extracted_data)
                save_and_download_json(extracted_data)

        if st.button("Convertir en CSV", type="primary", key="image_csv_button"): # Added key
            with st.spinner("📄 Conversion en CSV..."):
                # Pass document_type to extract_info_from_image
                extracted_data = extract_info_from_image(uploaded_file, selected_fields_str, document_type)
                df = pd.DataFrame(extracted_data.items(), columns=["Champ", "Valeur"])
                csv_filename = "extracted_data.csv"
                df.to_csv(csv_filename, index=False)

                st.success("✅ CSV exporté avec succès")
                st.download_button("⬇️ Télécharger CSV", open(csv_filename, "rb"), file_name=csv_filename, mime="text/csv", key="image_download_button") # Added key

