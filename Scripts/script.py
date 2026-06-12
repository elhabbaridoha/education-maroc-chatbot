import json
import google.generativeai as genai
import time

# Configuration de l'API (à remplacer par ta clé API)
genai.configure(api_key="AIzaSyAXdRilBGDuzoglgQ_reKi8aUn5A8EyWZM")
model = genai.GenerativeModel('gemini-1.5-flash')

# Exemple de données brutes issues de tes scripts de scraping
textes_scrapes = [
    "La plateforme Tawjihi permet aux bacheliers marocains de postuler aux écoles d'ingénieurs (ENSA, ENSAM) et aux écoles de commerce (ENCG) de manière centralisée.",
    # Ajoute ici des centaines de paragraphes issus de tes scrapes
]

dataset_final = []
current_id = 153 # Pour faire suite à tes ID existants

prompt_template = """
À partir du texte suivant issu du système éducatif marocain, génère 3 paires de questions/réponses en français et leur traduction exacte en arabe.
Renvoie UNIQUEMENT un tableau JSON valide avec la structure suivante pour chaque élément :
{{"id": "{id_base}", "question": "", "reponse": "", "question_ar": "", "reponse_ar": "", "niveau": "général", "categorie": "orientation", "source": "scraped_data", "langue": "bilingue"}}

Texte : {texte}
"""

for texte in textes_scrapes:
    try:
        # Appel à l'API pour générer le JSON
        response = model.generate_content(prompt_template.format(id_base=str(current_id).zfill(5), texte=texte))
        
        # Nettoyage et parsing du JSON renvoyé par l'IA
        json_string = response.text.strip().replace("```json", "").replace("```", "")
        paires = json.loads(json_string)
        
        # Mise à jour des IDs et ajout à la liste principale
        for paire in paires:
            paire["id"] = str(current_id).zfill(5)
            dataset_final.append(paire)
            current_id += 1
            
        time.sleep(2) # Pause pour éviter de dépasser les limites de l'API (rate limit)

    except Exception as e:
        print(f"Erreur lors du traitement du texte: {e}")

# Sauvegarde dans le fichier final
with open('dataset_genere.json', 'w', encoding='utf-8') as f:
    json.dump(dataset_final, f, ensure_ascii=False, indent=2)

print(f"{len(dataset_final)} nouvelles paires générées avec succès !")