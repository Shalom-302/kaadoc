import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from process import (
    possible_fields, 
    get_selected_check_point_fields, 
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
selected_document = st.selectbox("Sélectionnez un type de document", list(possible_fields.keys()))

selected_fields = {}

if selected_document:
    st.subheader(f"Champs à extraire pour {selected_document}")

    if selected_document == "check-point":
        selected_fields = get_selected_check_point_fields(possible_fields)
    else:
        selected_fields[selected_document] = st.multiselect(
            "Sélectionnez les informations à extraire :",
            options=possible_fields[selected_document],
            default=possible_fields[selected_document]
        )

    st.write("### Champs sélectionnés :")
    st.json(selected_fields)

# Traitement des fichiers
if uploaded_file:
    file_type = uploaded_file.type

    if "pdf" in file_type:
        st.success("📄 PDF uploaded successfully")
        if st.button("Convertir en JSON", type="primary"):
            with st.spinner("📄 Traitement du PDF..."):
                extracted_text = get_pdf_text([uploaded_file])
                text_chunks = get_text_chunks(extracted_text)
                get_vector_store(text_chunks)

                extracted_data = user_input(", ".join(selected_fields[selected_document]))

                st.subheader("Résultat des données en JSON")
                st.json(extracted_data)
                save_and_download_json(extracted_data)

        if st.button("Convertir en CSV", type="primary"):
            with st.spinner("📄 Conversion en CSV..."):
                extracted_data = user_input(selected_fields)
                df = pd.DataFrame(extracted_data.items(), columns=["Champ", "Valeur"])
                csv_filename = "extracted_data.csv"
                df.to_csv(csv_filename, index=False)

                st.success("✅ CSV exporté avec succès")
                st.download_button("⬇️ Télécharger CSV", open(csv_filename, "rb"), file_name=csv_filename, mime="text/csv")

    elif "image" in file_type:
        st.success("🖼 Image uploaded successfully")
        st.image(uploaded_file, caption="Image téléchargée", use_container_width=True)

        if st.button("Convertir en JSON", type="primary"):
            with st.spinner("📄 Traitement de l'image..."):
                extracted_data = extract_info_from_image(uploaded_file, selected_fields)
                st.subheader("Résultat des données en JSON")
                st.json(extracted_data)
                save_and_download_json(extracted_data)

        if st.button("Convertir en CSV", type="primary"):
            with st.spinner("📄 Conversion en CSV..."):
                extracted_data = extract_info_from_image(uploaded_file, selected_fields)
                df = pd.DataFrame(extracted_data.items(), columns=["Champ", "Valeur"])
                csv_filename = "extracted_data.csv"
                df.to_csv(csv_filename, index=False)

                st.success("✅ CSV exporté avec succès")
                st.download_button("⬇️ Télécharger CSV", open(csv_filename, "rb"), file_name=csv_filename, mime="text/csv")
