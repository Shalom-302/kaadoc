import streamlit as st
from components import set_page_config, navbar, upload_file, extraction_options, apply_custom_css

def main():
    set_page_config()
    apply_custom_css()
    navbar()

    menu = ["🏠 Accueil", "🔍 Extraction", "📥 Téléchargement"]
    choice = st.sidebar.radio("📌 Navigation", menu)

    if choice == "🏠 Accueil":
        st.title("🏠 Bienvenue sur l'application")
        st.write("Téléversez un fichier et commencez l'extraction.")

    elif choice == "🔍 Extraction":
        st.title("🔍 Extraction des Données")
        uploaded_file = upload_file()

        if uploaded_file:
            extraction_type = extraction_options()
            st.success(f"Mode d'extraction sélectionné : {extraction_type}")
            st.write("L'extraction va commencer...")

    elif choice == "📥 Téléchargement":
        st.title("📥 Téléchargement")
        st.write("Ici, vous pourrez récupérer vos fichiers convertis en JSON/CSV.")

if __name__ == "__main__":
    main()
