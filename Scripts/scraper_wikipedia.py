import requests
from bs4 import BeautifulSoup
import json
import os
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# ─────────────────────────────────────────
# LISTE DES PAGES WIKIPEDIA À SCRAPER
# ─────────────────────────────────────────
pages_wikipedia = [

    # FRANÇAIS
    {"url": "https://fr.wikipedia.org/wiki/Baccalaur%C3%A9at_au_Maroc",                    "langue": "fr", "categorie": "bac"},
    {"url": "https://fr.wikipedia.org/wiki/Syst%C3%A8me_%C3%A9ducatif_marocain",           "langue": "fr", "categorie": "système éducatif"},
    {"url": "https://fr.wikipedia.org/wiki/Enseignement_sup%C3%A9rieur_au_Maroc",          "langue": "fr", "categorie": "université"},
    {"url": "https://fr.wikipedia.org/wiki/Universit%C3%A9_au_Maroc",                      "langue": "fr", "categorie": "université"},
    {"url": "https://fr.wikipedia.org/wiki/Classes_pr%C3%A9paratoires_au_Maroc",           "langue": "fr", "categorie": "CPGE"},
    {"url": "https://fr.wikipedia.org/wiki/Universit%C3%A9_Cadi_Ayyad",                    "langue": "fr", "categorie": "université"},
    {"url": "https://fr.wikipedia.org/wiki/Universit%C3%A9_Mohammed_V_de_Rabat",           "langue": "fr", "categorie": "université"},
    {"url": "https://fr.wikipedia.org/wiki/Universit%C3%A9_Hassan_II_de_Casablanca",       "langue": "fr", "categorie": "université"},
    {"url": "https://fr.wikipedia.org/wiki/Orientation_scolaire",                          "langue": "fr", "categorie": "orientation"},
    {"url": "https://fr.wikipedia.org/wiki/Minist%C3%A8re_de_l%27%C3%89ducation_nationale_(Maroc)", "langue": "fr", "categorie": "ministère"},

    # ARABE
    {"url": "https://ar.wikipedia.org/wiki/%D8%A7%D9%84%D8%AA%D8%B9%D9%84%D9%8A%D9%85_%D9%81%D9%8A_%D8%A7%D9%84%D9%85%D8%BA%D8%B1%D8%A8",     "langue": "ar", "categorie": "système éducatif"},
    {"url": "https://ar.wikipedia.org/wiki/%D8%A7%D9%84%D8%A8%D9%83%D8%A7%D9%84%D9%88%D8%B1%D9%8A%D8%A7_%D8%A7%D9%84%D9%85%D8%BA%D8%B1%D8%A8%D9%8A%D8%A9", "langue": "ar", "categorie": "bac"},
    {"url": "https://ar.wikipedia.org/wiki/%D8%AC%D8%A7%D9%85%D8%B9%D8%A9_%D8%A7%D9%84%D9%�%D9%82%D8%A7%D8%B6%D9%8A_%D8%B9%D9%8A%D8%A7%D8%B6", "langue": "ar", "categorie": "université"},
    {"url": "https://ar.wikipedia.org/wiki/%D8%A7%D9%84%D8%AA%D8%B9%D9%84%D9%8A%D9%85_%D8%A7%D9%84%D8%B9%D8%A7%D9%84%D9%8A_%D9%81%D9%8A_%D8%A7%D9%84%D9%85%D8%BA%D8%B1%D8%A8", "langue": "ar", "categorie": "université"},
]

# ─────────────────────────────────────────
# FONCTION D'EXTRACTION
# ─────────────────────────────────────────
def extraire_wikipedia(url, langue, categorie):
    """Extrait les sections h2/h3 + paragraphes d'une page Wikipedia."""
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Titre de la page
        titre = soup.find('h1').get_text(strip=True)

        # Contenu principal Wikipedia
        contenu = soup.find('div', {'id': 'mw-content-text'})
        if not contenu:
            return []

        donnees = []

        # Méthode 1 : sections h2/h3 + paragraphes suivants
        sections = contenu.find_all(['h2', 'h3'])
        for section in sections:
            titre_section = section.get_text(strip=True)

            # Ignorer les sections inutiles
            a_ignorer = ['notes', 'références', 'voir aussi', 'liens externes',
                        'bibliographie', 'annexes', 'sommaire', 'menu de navigation',
                        'ملاحظات', 'مراجع', 'وصلات خارجية']
            if any(x in titre_section.lower() for x in a_ignorer):
                continue

            # Paragraphes suivant ce titre
            reponse_parts = []
            for sibling in section.find_next_siblings():
                if sibling.name in ['h2', 'h3']:
                    break
                if sibling.name == 'p':
                    texte = sibling.get_text(strip=True)
                    # Nettoyer les références [1], [2]...
                    import re
                    texte = re.sub(r'\[\d+\]', '', texte).strip()
                    if len(texte) > 60:
                        reponse_parts.append(texte)

            reponse = " ".join(reponse_parts[:3])

            if titre_section and reponse and len(reponse) > 80:
                donnees.append({
                    "id": "",
                    "question": f"{titre_section} - {titre}" if langue == "fr"
                                else f"{titre_section}",
                    "reponse": reponse,
                    "question_ar": "",
                    "reponse_ar": "",
                    "niveau": "général",
                    "categorie": categorie,
                    "source": f"Wikipedia {'FR' if langue == 'fr' else 'AR'}",
                    "langue": langue
                })

        # Méthode 2 : si pas assez de sections → paragraphes directs
        if len(donnees) < 3:
            import re
            paragraphes = [
                re.sub(r'\[\d+\]', '', p.get_text(strip=True))
                for p in contenu.find_all('p')
                if len(p.get_text(strip=True)) > 100
            ]
            for para in paragraphes[:8]:
                donnees.append({
                    "id": "",
                    "question": titre,
                    "reponse": para,
                    "question_ar": "",
                    "reponse_ar": "",
                    "niveau": "général",
                    "categorie": categorie,
                    "source": f"Wikipedia {'FR' if langue == 'fr' else 'AR'}",
                    "langue": langue
                })

        print(f"   ✅ {titre} → {len(donnees)} paires")
        return donnees

    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return []

# ─────────────────────────────────────────
# LANCEMENT
# ─────────────────────────────────────────
os.makedirs("data/raw", exist_ok=True)
nouvelles_donnees = []

print("🚀 Scraping Wikipedia...\n")

for page in pages_wikipedia:
    print(f"📡 {page['url'][:60]}...")
    paires = extraire_wikipedia(page['url'], page['langue'], page['categorie'])
    nouvelles_donnees.extend(paires)
    time.sleep(1)  # Pause polie

# ─────────────────────────────────────────
# FUSIONNER AVEC DATASET EXISTANT
# ─────────────────────────────────────────
# Charger le dataset propre existant
with open("data/clean/dataset_propre.json", "r", encoding="utf-8") as f:
    dataset_existant = json.load(f)

# Fusionner
dataset_final = dataset_existant + nouvelles_donnees

# Réindexer les IDs
for i, item in enumerate(dataset_final):
    item["id"] = str(i + 1).zfill(4)

# ─────────────────────────────────────────
# SAUVEGARDER
# ─────────────────────────────────────────
chemin = "data/clean/dataset_propre.json"
with open(chemin, "w", encoding="utf-8") as f:
    json.dump(dataset_final, f, ensure_ascii=False, indent=4)

# ─────────────────────────────────────────
# RÉSUMÉ
# ─────────────────────────────────────────
print(f"\n{'='*50}")
print(f"✅ Wikipedia scraping terminé !")
print(f"📊 Nouvelles paires Wikipedia : {len(nouvelles_donnees)}")
print(f"📊 Dataset existant : {len(dataset_existant)}")
print(f"📊 TOTAL FINAL : {len(dataset_final)} paires")
print(f"📁 Sauvegardé : {chemin}")

print(f"\n📋 Par catégorie :")
categories = {}
for item in dataset_final:
    cat = item["categorie"]
    categories[cat] = categories.get(cat, 0) + 1
for cat, count in sorted(categories.items()):
    print(f"   {cat:25} : {count} entrées")