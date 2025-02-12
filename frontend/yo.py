import pandas as pd

# Création d'un dictionnaire
data = {
    "Nom": ["Alice", "Bob", "Charlie"],
    "Âge": [25, 30, 35],
    "Ville": ["Paris", "Lyon", "Marseille"]
}

# Création d'un DataFrame
df = pd.DataFrame(data)
# print(data)

# Sauvegarde en fichier CSV
 # index=False pour ne pas ajouter l'index dans le fichier
hey = df.to_csv("fichier.csv", index=False)  
print("Fichier CSV généré avec succès !")

with open ("fichier.csv", "r") as f :
    print(f.read())