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

# Initialize Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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
    """Génère un prompt basé sur les infos sélectionnées (unused in this timesheet context)"""
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
    """Extrait les infos sélectionnées directement depuis le texte (unused in this timesheet context)"""
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
 
    "Recap_Hebdo": [
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
   "Timesheet": [  # New key for Timesheet data
        "Employee Schedule (per employee):",
        "   - Employee Name",
        "   - Days Schedule:",
        "      - ven 31",
        "      - sam 01",
        "      - dim 02",
        "      - lun 03",
        "      - mar 04",
        "      - mer 05",
        "      - jeu 06",
        "      - ven 07",
        "      - sam 08",
        "      - dim 09",
        "      - lun 10",
        "      - mar 11",
        "      - mer 12",
        "      - jeu 13",
        "Totals:",
        "   - TOTAL_M",
        "   - TOTAL_M2",
        "   - TOTAL_M3",
        "   - TOTAL_M4",
        "   - TOTAL_A"
    ],
    "PointageMois": [
        "Header Information:",
        "   - Service",
        "   - Statut",
        "   - Month and Year",
        "Employee Pointage Data:",
        "   - Employee ID",
        "   - Employee Name",
        "   - Daily Pointage:",
        "      - 15-déc",
        "      - 16-déc",
        "      - 17-déc",
        "      - 18-déc",
        "      - 19-déc",
        "      - 20-déc",
        "      - 21-déc",
        "      - 22-déc",
        "      - 23-déc",
        "      - 24-déc",
        "      - 25-déc",
        "      - 26-déc",
        "      - 27-déc",
        "      - 28-déc",
        "      - 29-déc",
        "      - 30-déc",
        "      - ##/# (End of Month Day)"
    ],
    "FichePointageMensuel": [
        "Document Header", # "FICHE DE POINTAGE MENSUEL" -  though less crucial to extract as it's constant
        "Month and Year", # "Janvier 2024"
        "Employee Daily Hours Table:",
        "   - Employee Names (Column Headers)", # List of employee names
        "   - Daily Hours Data:",
        "      - 1", "      - 2", "      - 3", "      - 4", "      - 5", "      - 6", "      - 7", "      - 8", "      - 9", "      - 10",
        "      - 11", "      - 12", "      - 13", "      - 14", "      - 15", "      - 16", "      - 17", "      - 18", "      - 19", "      - 20",
        "      - 21", "      - 22", "      - 23", "      - 24", "      - 25", "      - 26", "      - 27", "      - 28", "      - 29", "      - 30", "      - 31",
        "Totals Section:",
        "   - TOTAL 1",
        "   - H. Normales",
        "   - H.S à 15%",
        "   - H.S à 25%",
        "   - H.S à 50%",
        "   - H.S à 75%",
        "   - H.S à 100%",
        "   - Nbre Panier",
        "   - Nbre Personnes",
        "   - Total H.S",
        "   - Nbres Jours",
        "Right Side Information:",
        "   - CLIENT",
        "   - EPC CI",
        "   - PERIODE",
        "   - POSTE OCCUPE",
        "   - LIEU DE TRAVAIL",
        "   - TIETTO",
        "   - SECTION",
        "   - CACHET ET SIGNATURE",
        "   - Exceliam SIGNATURE"
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
                key="checkpoint_employee_fields", # Unique key
                default=possible_fields["check-point"]["Employé"]

            )
            if selected_employe_fields:
                selected_fields["Employé"] = selected_employe_fields


            # Sélection des semaines
            selected_shifts = st.multiselect(
                "Sélectionnez les semaines :",
                options=list(possible_fields["check-point"]["Horaires"].keys()),
                key="checkpoint_shifts", # Unique key
                default=list(possible_fields["check-point"]["Horaires"].keys())
            )

            horaires_selection = {}
            for shift in selected_shifts:
                selected_days = st.multiselect(
                    f"Sélectionnez les jours pour {shift} :",
                    options=possible_fields["check-point"]["Horaires"][shift],
                    key=f"checkpoint_days_{shift}", # Unique key with shift name
                    default=possible_fields["check-point"]["Horaires"][shift]
                )

                day_selection = {}
                for day in selected_days:
                    selected_hours = st.multiselect(
                        f"Sélectionnez les horaires pour {day} ({shift}) :",
                        options=["Arrivée", "Départ","pause","reprise","emargement","observation"],
                        key=f"checkpoint_hours_{shift}_{day}", # Unique key with shift and day
                        default=["Arrivée", "Départ","pause","reprise","emargement","observation"]
                    )
                    if selected_hours:
                        day_selection[day] = selected_hours

                if day_selection:
                    horaires_selection[shift] = day_selection

            if horaires_selection:
                selected_fields["Horaires"] = horaires_selection

            return selected_fields



selected_fields_str_checkpoint= get_selected_check_point_fields(possible_fields)

def get_selected_timesheet_fields(possible_fields):
    """
    Creates a Streamlit UI to select fields from the Timesheet structure
    defined in possible_fields.

    Args:
        possible_fields (dict): The dictionary containing possible fields,
                                including the "Timesheet" structure.

    Returns:
        dict: A dictionary containing the selected timesheet fields, structured
              for data extraction.
    """
    selected_fields = {}
    timesheet_fields = possible_fields.get("Timesheet", []) # Get Timesheet fields or empty list if not found

    if not timesheet_fields:
        st.warning("Timesheet fields not found in possible_fields.")
        return selected_fields

    # --- Employee Schedule Selection ---
    if "Employee Schedule (per employee):" in timesheet_fields:
        st.subheader("Sélectionner les champs Employé:")
        select_employee_schedule = st.checkbox("Sélectionner la section 'Employee Schedule'", value=True, key="timesheet_employee_schedule_section") # Unique key
        # Option to select the whole section

        if select_employee_schedule:
            selected_employee_fields = {}

            # Employee Name selection
            if "   - Employee Name" in timesheet_fields:
                select_employee_name = st.checkbox("Nom de l'Employé", value=True, key="timesheet_employee_name") # Unique key
                if select_employee_name:
                    selected_employee_fields["Employee Name"] = True # Just a flag to indicate selection

            # Days Schedule Selection
            if "   - Days Schedule:" in timesheet_fields:
                select_days_schedule = st.checkbox("Horaires par Jour", value=True, key="timesheet_days_schedule_section") # Unique key
                if select_days_schedule:
                    selected_days_fields = {}
                    days_list_start_index = timesheet_fields.index("      - ven 31") # Find the start of days list

                    days_options = []
                    for field in timesheet_fields[days_list_start_index:]:
                        if field.startswith("      - "):
                            days_options.append(field.replace("      - ", "").strip())

                    selected_days = st.multiselect(
                        "Sélectionner les jours à extraire :",
                        options=days_options,
                        default=days_options, # Default to all days
                        key="timesheet_selected_days" # Unique key
                    )
                    if selected_days:
                        selected_days_fields["Days"] = selected_days
                    selected_employee_fields["Days Schedule"] = selected_days_fields # Group days under "Days Schedule"

            if selected_employee_fields:
                selected_fields["Employee Schedule"] = selected_employee_fields


    # --- Totals Selection ---
    if "Totals:" in timesheet_fields:
        st.subheader("Sélectionner les champs Totaux:")
        select_totals_section = st.checkbox("Sélectionner la section 'Totals'", value=False, key="timesheet_totals_section") # Unique key
        # Option to select totals section

        if select_totals_section:
            selected_totals_fields = {}
            totals_list_start_index = timesheet_fields.index("   - TOTAL_M") # Find start of totals list

            totals_options = []
            for field in timesheet_fields[totals_list_start_index:]:
                if field.startswith("   - "):
                    totals_options.append(field.replace("   - ", "").strip())

            selected_totals = st.multiselect(
                "Sélectionner les totaux à extraire :",
                options=totals_options,
                default=totals_options, # Default to all totals
                key="timesheet_selected_totals" # Unique key
            )
            if selected_totals:
                selected_totals_fields["Totals"] = selected_totals
            if selected_totals_fields:
                selected_fields["Totals"] = selected_totals_fields

    return selected_fields

# Appel de la fonction pour obtenir les données Timesheet
selected_fields_timesheet = get_selected_timesheet_fields(possible_fields)

def get_selected_pointage_mois_fields(possible_fields):
    """
    Creates a Streamlit UI to select fields from the PointageMois structure.
    """
    selected_fields = {}
    pointage_mois_fields = possible_fields.get("PointageMois", [])

    if not pointage_mois_fields:
        st.warning("PointageMois fields not found in possible_fields.")
        return selected_fields

    # --- Header Information Selection ---
    if "Header Information:" in pointage_mois_fields:
        st.subheader("Sélectionner les champs d'en-tête:")
        select_header_section = st.checkbox("Sélectionner la section 'Header Information'", key="pointage_header_section", value=False)

        if select_header_section:
            selected_header_fields = {}
            header_fields_list_start_index = pointage_mois_fields.index("   - Service")

            header_options = []
            for field in pointage_mois_fields[header_fields_list_start_index:]:
                if field.startswith("   - "):
                    if "Employee Pointage Data" in field: # Stop at the next section
                        break
                    header_options.append(field.replace("   - ", "").strip())

            selected_header_items = st.multiselect(
                "Sélectionner les informations d'en-tête à extraire :",
                options=header_options,
                default=header_options, # Default to all header info
                key="pointage_selected_header_fields"
            )
            if selected_header_items:
                selected_header_fields["Header Items"] = selected_header_items
            if selected_header_fields:
                selected_fields["Header Information"] = selected_header_fields


    # --- Employee Pointage Data Selection ---
    if "Employee Pointage Data:" in pointage_mois_fields:
        st.subheader("Sélectionner les champs de données de pointage:")
        select_pointage_data_section = st.checkbox("Sélectionner la section 'Employee Pointage Data'", key="pointage_data_section", value=True)

        if select_pointage_data_section:
            selected_pointage_data_fields = {}

            # Employee ID and Name (always include these)
            selected_pointage_data_fields["Employee ID"] = True
            selected_pointage_data_fields["Employee Name"] = True

            # Daily Pointage Selection
            if "   - Daily Pointage:" in pointage_mois_fields:
                select_daily_pointage = st.checkbox("Pointage Quotidien", key="pointage_daily_section", value=True)
                if select_daily_pointage:
                    selected_daily_fields = {}
                    days_list_start_index = pointage_mois_fields.index("      - 15-déc")

                    days_options = []
                    for field in pointage_mois_fields[days_list_start_index:]:
                        if field.startswith("      - "):
                            days_options.append(field.replace("      - ", "").strip())

                    selected_days = st.multiselect(
                        "Sélectionner les jours de pointage à extraire :",
                        options=days_options,
                        default=days_options, # Default to all days
                        key="pointage_selected_days"
                    )
                    if selected_days:
                        selected_daily_fields["Days"] = selected_days
                    selected_pointage_data_fields["Daily Pointage"] = selected_daily_fields

            if selected_pointage_data_fields:
                selected_fields["Employee Pointage Data"] = selected_pointage_data_fields

    return selected_fields
selected_fields_pointage_mois= get_selected_pointage_mois_fields(possible_fields)


def get_selected_fiche_pointage_mensuel_fields(possible_fields):
    """
    Creates a Streamlit UI to select fields from the FichePointageMensuel structure.
    """
    selected_fields = {}
    fiche_pointage_mensuel_fields = possible_fields.get("FichePointageMensuel", [])

    if not fiche_pointage_mensuel_fields:
        st.warning("FichePointageMensuel fields not found in possible_fields.")
        return selected_fields

    # --- Document Header Selection --- (Optional for now, can add later if needed)
    # For Document Header and Month/Year, we might just always extract them, or add simple checkboxes later if selection is needed.

    # --- Employee Daily Hours Table Selection ---
    if "Employee Daily Hours Table:" in fiche_pointage_mensuel_fields:
        st.subheader("Sélectionner les champs de la table des heures :")
        select_table_section = st.checkbox("Sélectionner la section 'Employee Daily Hours Table'", key="fiche_pointage_table_section", value=True)

        if select_table_section:
            selected_table_fields = {}

            # Employee Names (Column Headers) - Usually always needed
            selected_table_fields["Employee Names (Column Headers)"] = True # Just a flag

            # Daily Hours Data Selection
            if "   - Daily Hours Data:" in fiche_pointage_mensuel_fields:
                select_daily_hours_data = st.checkbox("Données d'heures quotidiennes", key="fiche_pointage_daily_hours_section", value=True)
                if select_daily_hours_data:
                    selected_daily_hours_fields = {}
                    days_list_start_index = fiche_pointage_mensuel_fields.index("      - 1")

                    days_options = []
                    for field in fiche_pointage_mensuel_fields[days_list_start_index:]:
                        if field.startswith("      - "):
                            if "Totals Section" in field: # Stop at the next section
                                break
                            days_options.append(field.replace("      - ", "").strip())

                    selected_days = st.multiselect(
                        "Sélectionner les jours pour les données d'heures :",
                        options=days_options,
                        default=days_options, # Default to all days
                        key="fiche_pointage_selected_days"
                    )
                    if selected_days:
                        selected_daily_hours_fields["Days"] = selected_days
                    selected_table_fields["Daily Hours Data"] = selected_daily_hours_fields

            if selected_table_fields:
                selected_fields["Employee Daily Hours Table"] = selected_table_fields


    # --- Totals Section Selection ---
    if "Totals Section:" in fiche_pointage_mensuel_fields:
        st.subheader("Sélectionner les champs de la section Totaux:")
        select_totals_section = st.checkbox("Sélectionner la section 'Totals Section'", key="fiche_pointage_totals_section", value=False)

        if select_totals_section:
            selected_totals_fields = {}
            totals_list_start_index = fiche_pointage_mensuel_fields.index("   - TOTAL 1")
            totals_options = []

            for field in fiche_pointage_mensuel_fields[totals_list_start_index:]:
                if field.startswith("   - "):
                    if "Right Side Information" in field: # Stop at the next section
                        break
                    totals_options.append(field.replace("   - ", "").strip())


            selected_totals = st.multiselect(
                "Sélectionner les totaux à extraire :",
                options=totals_options,
                default=totals_options, # Default to all totals
                key="fiche_pointage_selected_totals"
            )
            if selected_totals:
                selected_totals_fields["Totals"] = selected_totals
            if selected_totals_fields:
                selected_fields["Totals Section"] = selected_totals_fields


    # --- Right Side Information Selection ---
    if "Right Side Information:" in fiche_pointage_mensuel_fields:
        st.subheader("Sélectionner les champs d'informations du côté droit:")
        select_right_side_section = st.checkbox("Sélectionner la section 'Right Side Information'", key="fiche_pointage_right_side_section", value=False)

        if select_right_side_section:
            selected_right_side_fields = {}
            right_side_list_start_index = fiche_pointage_mensuel_fields.index("   - CLIENT")
            right_side_options = []

            for field in fiche_pointage_mensuel_fields[right_side_list_start_index:]:
                if field.startswith("   - "):
                    right_side_options.append(field.replace("   - ", "").strip())

            selected_right_side_items = st.multiselect(
                "Sélectionner les informations du côté droit à extraire :",
                options=right_side_options,
                default=right_side_options, # Default to all right side info
                key="fiche_pointage_selected_right_side_fields"
            )
            if selected_right_side_items:
                selected_right_side_fields["Right Side Items"] = selected_right_side_items
            if selected_right_side_fields:
                selected_fields["Right Side Information"] = selected_right_side_fields


    return selected_fields
Fiche_Pointage_Mensuel = get_selected_fiche_pointage_mensuel_fields(possible_fields)
def extract_info_from_image(uploaded_file, selected_fields_str, document_type):
    """Envoie l'image à Gemini et retourne les informations extraites"""
    # Génération dynamique du prompt basé sur les champs sélectionnés

    if document_type == "Timesheet":
        prompt = f"""
**Analyze the provided Timesheet image and extract the following information in a structured JSON format.**

**Instructions:**

1.  **Identify Employees and Schedules:** For each employee listed in the timesheet, extract their schedule for the following days (if selected by the user): {selected_fields_str}.  If "Employee Name" is selected, extract the employee's name. For each selected day, extract the corresponding schedule value (e.g., "OFF", "M2", "A", "M", "N", "C").

2.  **Identify Totals:** If "Totals" are selected, extract the values for the following totals types (if selected by the user) for each day: {selected_fields_str}. Extract the numerical value associated with each selected total type and day.

3.  **JSON Output Format:**  **Return a STRICTLY VALID JSON object with the following structure:**

    ```json
    {{
      "employees_schedule": {{
        "EMPLOYEE_ID_1": {{
          "name": "EMPLOYEE_NAME_1",
          "ven 31": "SCHEDULE_VALUE_VEN_31",
          "sam 01": "SCHEDULE_VALUE_SAM_01",
          ... (and so on for selected days) ...
        }},
        "EMPLOYEE_ID_2": {{
          "name": "EMPLOYEE_NAME_2",
          "ven 31": "SCHEDULE_VALUE_VEN_31",
          "sam 01": "SCHEDULE_VALUE_SAM_01",
          ... (and so on for selected days) ...
        }},
        ... (and so on for all employees) ...
      }},
      "totals": {{
        "TOTAL_M": {{
          "ven 31": "TOTAL_M_VALUE_VEN_31",
          "sam 01": "TOTAL_M_VALUE_SAM_01",
          ... (and so on for selected days) ...
        }},
        "TOTAL_M2": {{
          "ven 31": "TOTAL_M2_VALUE_VEN_31",
          "sam 01": "TOTAL_M2_VALUE_SAM_01",
          ... (and so on for selected days) ...
        }},
        ... (and so on for all selected totals types) ...
      }}
    }}
    ```

    *   **EMPLOYEE_ID_X:** Use employee IDs "1", "2", "3", ... as keys.
    *   **EMPLOYEE_NAME_X:** Extract the full name of the employee.
    *   **SCHEDULE_VALUE_DAY:** Extract the schedule value for the corresponding day (e.g., "OFF", "M2", etc.).
    *   **TOTAL_TYPE:** Use the total types like "TOTAL_M", "TOTAL_M2", etc., as keys.
    *   **TOTAL_TYPE_VALUE_DAY:** Extract the numerical value for the total type on the corresponding day (e.g., "3,00", "4,00", etc.).

4.  **Data Absence:** If a schedule value or total value is missing or unreadable in the image, use an empty string `""` as the value in the JSON.

5.  **Strict JSON:** Ensure the output is valid JSON and contains **ONLY** the JSON object. No extra text or explanations outside the JSON structure.

**Provided Timesheet Image:**  [The image you provided previously]

**User Selected Fields (Example, adjust based on actual selections):**
{selected_fields_timesheet}


**Example JSON Output (based on the image and selections):**
(The model should generate JSON output in the structure described above, filled with the extracted values from the image, not just the selections)
    """
    elif document_type == "check-point":
         prompt = f"""
Analyse ce document check-point et extraits uniquement les informations suivantes : {selected_fields_str}.
Instructions en respectant la présentation et l'organisation du document dans l’image.
verifie aussi les emargements et les observations qui sont en signature manuscrites
Instructions :

Génére un JSON strictement valide, fidèle à la structure des données présentes dans l’image.
Ne laisse aucune donnée de côté : tous les employés et toutes les informations doivent être capturés.
Respecte scrupuleusement la hiérarchie et le format des clés et valeurs visibles dans l’image.
Aucun texte en dehors du JSON : ne retourne que le JSON brut.
Si des valeurs sont absentes ou illisibles, conserve la structure avec des valeurs vides ("" ou null).
    """
    elif document_type == "FichePointageMensuel": 
        prompt = f"""
**Analyze the provided "Fiche de Pointage Mensuel" (Monthly Pointing Sheet) image and extract the following information in a structured JSON format.**

**Instructions:**

1.  **Header Information Extraction:** If "Header Information" is selected, extract **ALL** of the following header fields that the user selected: {selected_fields_str}.  Specifically extract the text values for "Service", "Statut", and "Month and Year". If the section is selected, ensure to find and extract values for all the listed header items that the user also selected.

2.  **Employee Daily Hours Data Extraction:**
    *   **Employee Names:** Extract the employee names from the **column headers** of the table. These names will be used as keys in the JSON structure.
    *   **Daily Hours:** For each employee and each day selected by the user ({Fiche_Pointage_Mensuel}), extract the corresponding hours value from the table. Use the day numbers (1, 2, 3, ..., 31) as keys for the daily hours.

3.  **Totals Section Extraction:** If "Totals Section" is selected, extract **ALL** of the following totals fields that the user selected: {selected_fields_str}.  Specifically extract the numerical value for each of these total types: "TOTAL 1", "H. Normales", "H.S à 15%", "H.S à 25%", "H.S à 50%", "H.S à 75%", "H.S à 100%", "Nbre Panier", "Nbre Personnes", "Total H.S", "Nbres Jours". If the section is selected, ensure to find and extract values for **ALL** of these listed total items that the user also selected.

4.  **Right Side Information Extraction:** If "Right Side Information" is selected, extract **ALL** of the following right-side information fields that the user selected: {selected_fields_str}. Specifically extract the text values for "CLIENT", "EPC CI", "PERIODE", "POSTE OCCUPE", "LIEU DE TRAVAIL", "TIETTO", "SECTION", "CACHET ET SIGNATURE", and "Exceliam SIGNATURE". If the section is selected, ensure to find and extract values for **ALL** of these listed right-side information items that the user also selected.

5.  **JSON Output Format:** **Return a STRICTLY VALID JSON object with the following structure:**

    ```json
    {{
      "header_information": {{
        "service": "SERVICE_VALUE",
        "statut": "STATUT_VALUE",
        "month_year": "MONTH_YEAR_VALUE"
      }},
      "employee_daily_hours": {{
        "EMPLOYEE_NAME_1": {{
          "1": "HOURS_DAY_1",
          "2": "HOURS_DAY_2",
          ... (and so on for selected days) ...
        }},
        "EMPLOYEE_NAME_2": {{
          "1": "HOURS_DAY_1",
          "2": "HOURS_DAY_2",
          ... (and so on for selected days) ...
        }},
        ... (and so on for all employees) ...
      }},
      "totals_section": {{
        "TOTAL 1": "TOTAL_1_VALUE",
        "H. Normales": "H_NORMALES_VALUE",
        ... (and so on for selected totals) ...
      }},
      "right_side_information": {{
        "CLIENT": "CLIENT_VALUE",
        "EPC CI": "EPC_CI_VALUE",
        ... (and so on for selected right side items) ...
      }}
    }}
    ```

    *   **SERVICE_VALUE, STATUT_VALUE, MONTH_YEAR_VALUE:** Extract the corresponding header information. If not selected, use empty strings `""`.
    *   **EMPLOYEE_NAME_X:** Use the extracted employee names as keys.
    *   **HOURS_DAY_Y:** Extract the hours value for the corresponding day.
    *   **TOTAL_TYPE_VALUE:** Extract the numerical value for the total type.
    *   **RIGHT_SIDE_ITEM_VALUE:** Extract the text value for the right-side information items.

6.  **Data Absence:** If any value is missing or unreadable, use an empty string `""` as the value in the JSON.

7.  **Strict JSON:** Ensure the output is valid JSON and contains **ONLY** the JSON object. No extra text or explanations outside the JSON structure.


**Example JSON Output:**
(The model should generate JSON output in the structure described above, filled with the extracted values from the image, not just the selections)
"""
    elif document_type == "PointageMois":  
        prompt = f"""
**Analyze the provided "Pointage du Mois" (Monthly Pointing) image and extract the following information in a structured JSON format.**

**Instructions:**

1.  **Header Information Extraction:** If "Header Information" is selected, extract the following from the header of the document (if selected by the user): {selected_fields_str}.  Extract the text values for "Service", "Statut", and "Month and Year".

2.  **Employee Pointage Data Extraction:** For each employee listed in the table, extract the following:
    *   **Employee ID:** Extract the number in the "N°" column as "employee_id".
    *   **Employee Name:** Extract the name from the "Nom & Prénoms" column as "employee_name".
    *   **Daily Pointage:** For each day selected by the user ({selected_fields_pointage_mois}), extract the corresponding pointage value (e.g., "P", "OB", "I 290 P", "860 P", "540 P", "900 P", "INT 900 INT", "####").  Use the dates (e.g., "15-déc", "16-déc", etc.) as keys for the daily pointage values.

3.  **JSON Output Format:** **Return a STRICTLY VALID JSON object with the following structure:**

    ```json
    {{
      "header_information": {{
        "service": "SERVICE_VALUE",
        "statut": "STATUT_VALUE",
        "month_year": "MONTH_YEAR_VALUE"
      }},
      "employee_pointage_data": {{
        "EMPLOYEE_ID_1": {{
          "employee_name": "EMPLOYEE_NAME_1",
          "15-déc": "POINTAGE_VALUE_15_DEC",
          "16-déc": "POINTAGE_VALUE_16_DEC",
          ... (and so on for selected days) ...
        }},
        "EMPLOYEE_ID_2": {{
          "employee_name": "EMPLOYEE_NAME_2",
          "15-déc": "POINTAGE_VALUE_15_DEC",
          "16-déc": "POINTAGE_VALUE_16_DEC",
          ... (and so on for selected days) ...
        }},
        ... (and so on for all employees) ...
      }}
    }}
    ```

    *   **SERVICE_VALUE, STATUT_VALUE, MONTH_YEAR_VALUE:** Extract the corresponding header information. If not selected, use empty strings `""`.
    *   **EMPLOYEE_ID_X:** Use employee IDs "1", "2", "3", ... as keys.
    *   **EMPLOYEE_NAME_X:** Extract the full name of the employee.
    *   **POINTAGE_VALUE_DAY:** Extract the pointage value for the corresponding day.

4.  **Data Absence:** If a pointage value or header information is missing or unreadable, use an empty string `""` as the value in the JSON.

5.  **Strict JSON:** Ensure the output is valid JSON and contains **ONLY** the JSON object. No extra text or explanations outside the JSON structure.



**Example JSON Output:**
(The model should generate JSON output in the structure described above, filled with the extracted values from the image, not just the selections)
               
"""

    else:
        prompt = f"""
Analyse ce document et extraits uniquement les informations suivantes : {selected_fields_str}.
Instructions en respectant la présentation et l'organisation du document dans l’image.
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


def main():
    st.set_page_config(page_title="Extraction de Données d'Images")
    st.header("Extraction de Données de Documents")

    document_type = st.selectbox(
        "Sélectionnez le type de document :",
        ["Timesheet", "check-point", "Resume", "Drive-Licence", "ID-Card", "Invoice", "Work-Schedule", "Work-Schedule-1"],
        key="document_type_selectbox" # Unique key for selectbox
    )

    uploaded_file = st.file_uploader("Télécharger une image du document", type=['png', 'jpg', 'jpeg'], key="file_uploader") # Unique key

    selected_fields_str = ""  # Initialize to empty string

    if document_type == "Timesheet":
        selected_fields_timesheet_variable = get_selected_timesheet_fields(possible_fields) # Use the variable here
        selected_fields_str_timesheet = json.dumps(selected_fields_timesheet_variable, ensure_ascii=False)
        selected_fields_str = selected_fields_str_timesheet # Assign to the general variable
    elif document_type == "check-point":
        selected_fields_checkpoint_variable = get_selected_check_point_fields(possible_fields)
        selected_fields_str_checkpoint_json = json.dumps(selected_fields_checkpoint_variable, ensure_ascii=False)
        selected_fields_str = selected_fields_str_checkpoint_json


    elif document_type == "Resume":
        selected_fields_str = json.dumps(possible_fields["Resume"]) # Example, adapt for UI selection if needed
    elif document_type == "Drive-Licence":
        selected_fields_str = json.dumps(possible_fields["Drive-Licence"]) # Example, adapt for UI selection if needed
    elif document_type == "ID-Card":
        selected_fields_str = json.dumps(possible_fields["ID-Card"]) # Example, adapt for UI selection if needed
    elif document_type == "Invoice":
        selected_fields_str = json.dumps(possible_fields["Invoice"]) # Example, adapt for UI selection if needed
    elif document_type == "Work-Schedule":
        selected_fields_str = json.dumps(possible_fields["Work-Schedule"]) # Example, adapt for UI selection if needed
    elif document_type == "Work-Schedule-1":
        selected_fields_str = json.dumps(possible_fields["Work-Schedule-1"]) # Example, adapt for UI selection if needed


    if uploaded_file is not None:
        if st.button("Extraire les informations", key="extract_button"): # Unique key for button
            with st.spinner("Extraction des informations..."):
                # Corrected function call to include document_type
                extracted_data = extract_info_from_image(uploaded_file, selected_fields_str, document_type)
                if extracted_data:
                    st.subheader("📊 Données extraites en JSON :")
                    st.json(extracted_data, expanded=False)
                    save_and_download_json(extracted_data)


if __name__ == '__main__':
    main()