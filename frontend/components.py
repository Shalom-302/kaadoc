import streamlit as st

def set_page_config():
    """Configure la page principale"""
    st.set_page_config(
        page_title="Extraction & Conversion",
        page_icon="📄",
        layout="wide"
    )

def navbar():
    """Barre de navigation en haut"""
    st.markdown("""
        <style>
            .navbar {
                background-color: #4CAF50;
                padding: 10px;
                text-align: center;
                font-size: 20px;
                color: white;
                border-radius: 10px;
                margin-bottom: 20px;
            }
        </style>
        <div class='navbar'>🚀 Extraction et Conversion de Données</div>
    """, unsafe_allow_html=True)

def upload_file():
    """Composant pour téléverser un fichier"""
    st.sidebar.header("📂 Téléverser un fichier")
    uploaded_file = st.sidebar.file_uploader(
        "Choisissez un fichier",
        type=["pdf", "png", "jpg", "jpeg", "txt", "mp3", "mp4"]
    )
    return uploaded_file

def extraction_options():
    """Options pour choisir l'extraction"""
    return st.radio("📌 Choisissez le type d'extraction :", ["Extraction complète", "Sélection manuelle"])

def apply_custom_css():
    """Ajoute du CSS personnalisé pour un meilleur rendu"""
    st.markdown("""
        <style>
        body { font-family: Arial, sans-serif; }
        .stButton>button { 
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
        }
        </style>
    """, unsafe_allow_html=True)
