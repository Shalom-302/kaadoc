



import streamlit as st

def get_selected_fields(possible_fields):
    selected_fields = {}

    # Sélection des champs Employé
    selected_employe_fields = st.multiselect(
        "Sélectionnez les champs Employé :",
        options=possible_fields["check-point"]["Employé"]
    )
    if selected_employe_fields:
        selected_fields["Employé"] = selected_employe_fields

    # Sélection des semaines
    selected_shifts = st.multiselect(
        "Sélectionnez les semaines :",
        options=list(possible_fields["check-point"]["Horaires"].keys())
    )

    horaires_selection = {}
    for shift in selected_shifts:
        selected_days = st.multiselect(
            f"Sélectionnez les jours pour {shift} :",
            options=possible_fields["check-point"]["Horaires"][shift]
        )

        day_selection = {}
        for day in selected_days:
            selected_hours = st.multiselect(
                f"Sélectionnez les horaires pour {day} ({shift}) :",
                options=["Arrivée", "Départ"]
            )
            if selected_hours:
                day_selection[day] = selected_hours

        if day_selection:
            horaires_selection[shift] = day_selection

    if horaires_selection:
        selected_fields["Horaires"] = horaires_selection

    return selected_fields  # Retourne la structure des champs sélectionnés

# Exemple d'utilisation :
possible_fields = {
    "check-point": {
        "Employé": ["Nom", "Poste", "ID"],
        "Horaires": {
            "Semaine 1": ["Lundi", "Mardi"],
            "Semaine 2": ["Mercredi", "Jeudi"]
        }
    }
}

selected_data = get_selected_fields(possible_fields)

# Envoi à Gemini
import json
import requests

url = "https://api.gemini.com/extract"
headers = {"Content-Type": "application/json"}
payload = json.dumps({"data": selected_data})

response = requests.post(url, headers=headers, data=payload)

# Affichage de la réponse de Gemini
st.write(response.json())
