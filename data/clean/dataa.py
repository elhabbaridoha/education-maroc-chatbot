from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
import os

# ─────────────────────────────────────────
# CONFIGURATION DU NAVIGATEUR
# ─────────────────────────────────────────
def creer_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Décommente pour mode invisible
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=fr-FR")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

# ─────────────────────────────────────────
# SCRAPER GÉNÉRIQUE
# ─────────────────────────────────────────
def scraper_page(driver, url, attente=3):
    """Ouvre une page et retourne son HTML."""
    try:
        driver.get(url)
        time.sleep(attente)  # Attendre que la page charge
        return driver.page_source
    except Exception as e:
        print(f"❌ Erreur sur {url} : {e}")
        return None

# ─────────────────────────────────────────
# EXTRACTEUR DE CONTENU
# ─────────────────────────────────────────
def extraire_paires(html, source_name):
    """Extrait des paires question/réponse depuis le HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    donnees = []

    # Titre de la page = question principale
    titre = soup.find('h1')
    titre_texte = titre.get_text(strip=True) if titre else source_name

    # Chercher sections h2/h3 + paragraphes associés
    sections = soup.find_all(['h2', 'h3'])

    for section in sections:
        question = section.get_text(strip=True)
        
        # Récupérer les paragraphes qui suivent ce titre
        reponse_parts = []
        for sibling in section.find_next_siblings():
            if sibling.name in ['h2', 'h3']:
                break
            if sibling.name == 'p':
                texte = sibling.get_text(strip=True)
                if len(texte) > 40:
                    reponse_parts.append(texte)

        reponse = " ".join(reponse_parts[:3])

        if question and reponse:
            donnees.append({
                "id": "",  # sera rempli après
                "question": question,
                "reponse": reponse,
                "question_ar": "",
                "reponse_ar": "",
                "niveau": "général",
                "categorie": "général",
                "source": source_name,
                "langue": "fr"
            })

    # Si aucune section trouvée → prendre les paragraphes directs
    if not donnees:
        paragraphes = [
            p.get_text(strip=True)
            for p in soup.find_all('p')
            if len(p.get_text(strip=True)) > 80
        ]
        for para in paragraphes[:5]:
            donnees.append({
                "id": "",
                "question": titre_texte,
                "reponse": para,
                "question_ar": "",
                "reponse_ar": "",
                "niveau": "général",
                "categorie": "général",
                "source": source_name,
                "langue": "fr"
            })

    return donnees

# ─────────────────────────────────────────
# LISTE DES SITES À SCRAPER
# ─────────────────────────────────────────
sites = [
    # Ministère de l'Éducation
    {"url": "https://www.men.gov.ma/Fr/Pages/Accueil.aspx",       "nom": "men.gov.ma FR"},
    {"url": "https://www.men.gov.ma/Ar/Pages/Accueil.aspx",       "nom": "men.gov.ma AR"},

    # Tawjih
    {"url": "https://www.tawjihnet.net/actualites",               "nom": "tawjihnet"},
    {"url": "https://www.tawjihnet.net/bac",                      "nom": "tawjihnet-bac"},

    # Enseignement supérieur
    {"url": "https://www.enssup.gov.ma/fr",                       "nom": "enssup FR"},
    {"url": "https://www.enssup.gov.ma/ar",                       "nom": "enssup AR"},

    # CNF
    {"url": "https://cnf.uca.ma",                                 "nom": "CNF"},

    # Universités
    {"url": "https://www.uca.ma",                                 "nom": "UCA Marrakech"},
    {"url": "https://www.um5.ac.ma",                              "nom": "UM5 Rabat"},
    {"url": "https://www.uae.ac.ma",                              "nom": "UAE Tétouan"},
]

# ─────────────────────────────────────────
# LANCEMENT DU SCRAPING
# ─────────────────────────────────────────
os.makedirs("data/raw", exist_ok=True)
corpus_brut = []
driver = creer_driver()

print("🚀 Démarrage du scraping...\n")

for site in sites:
    print(f"📡 Scraping : {site['nom']} ({site['url']})")
    html = scraper_page(driver, site['url'], attente=4)

    if html:
        paires = extraire_paires(html, site['nom'])
        corpus_brut.extend(paires)
        print(f"   ✅ {len(paires)} paires extraites")
    else:
        print(f"   ❌ Échec")

    time.sleep(3)  # Pause entre chaque site

driver.quit()

# ─────────────────────────────────────────
# AJOUT DES IDs + SAUVEGARDE
# ─────────────────────────────────────────
for i, item in enumerate(corpus_brut):
    item["id"] = str(i + 1).zfill(4)

chemin = "data/raw/data_collectee.json"
with open(chemin, "w", encoding="utf-8") as f:
    json.dump(corpus_brut, f, ensure_ascii=False, indent=4)

print(f"\n{'='*50}")
print(f"✅ Scraping terminé !")
print(f"📊 Total collecté : {len(corpus_brut)} paires")
print(f"📁 Sauvegardé dans : {chemin}")
print(f"{'='*50}")