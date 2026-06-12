import json
import google.generativeai as genai
import time
import os

# ─── CONFIGURATION ───────────────────────────────
API_KEY = "AIzaSyDDTV7J_XO3b2T5SAkkxKYGSXBdajuPP3g"  # Nouvelle clé Google AI Studio
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

chemin_dataset = "data/final/dataset_final.json"

if not os.path.exists(chemin_dataset):
    print(f"[ERREUR] Fichier introuvable : {chemin_dataset}")
    exit()

with open(chemin_dataset, "r", encoding="utf-8") as f:
    dataset = json.load(f)

print(f"Dataset chargé : {len(dataset)} paires")

OBJECTIF_PAIRES = 10000
paires_par_appel = 10  # Réduit pour respecter le quota

thematiques = [
    {"niveau": "supérieur", "categorie": "concours", "sujet": "Concours EST, FST, ENSA au Maroc"},
    {"niveau": "baccalauréat", "categorie": "examens", "sujet": "Examens du Bac marocain régional et national"},
    {"niveau": "supérieur", "categorie": "orientation", "sujet": "Filières IA et informatique au Maroc"},
    {"niveau": "général", "categorie": "bourses", "sujet": "Bourses Minhaty et cités universitaires Maroc"},
    {"niveau": "formation professionnelle", "categorie": "concours", "sujet": "OFPPT filières et diplômes Maroc"},
    {"niveau": "université", "categorie": "inscription", "sujet": "Inscription université publique Maroc"},
    {"niveau": "bac", "categorie": "filières", "sujet": "Filières Bac Sciences Maths SVT Maroc"},
    {"niveau": "post-bac", "categorie": "orientation", "sujet": "CPGE et grandes écoles marocaines"},
]

prompt_template = """Tu es expert du système éducatif marocain.
Génère exactement {nombre} paires question/réponse bilingues sur : {sujet}
Renvoie UNIQUEMENT un tableau JSON valide, sans markdown.
Format :
[{{"id":"TEMP","question":"...?","reponse":"...","question_ar":"...؟","reponse_ar":"...","niveau":"{niveau}","categorie":"{categorie}","source":"gemini_api","langue":"bilingue"}}]"""

print("\n--- Augmentation automatique ---")
index_theme = 0
erreurs_consecutives = 0

try:
    while len(dataset) < OBJECTIF_PAIRES:
        theme = thematiques[index_theme % len(thematiques)]
        print(f"[{len(dataset)}/{OBJECTIF_PAIRES}] Thème : {theme['sujet'][:40]}...")

        prompt = prompt_template.format(
            nombre=paires_par_appel,
            sujet=theme["sujet"],
            niveau=theme["niveau"],
            categorie=theme["categorie"]
        )

        try:
            response = model.generate_content(prompt)
            texte = response.text.strip()

            # Nettoyage markdown
            if "```json" in texte:
                texte = texte.split("```json")[1].split("```")[0]
            elif "```" in texte:
                texte = texte.split("```")[1].split("```")[0]
            texte = texte.strip()

            nouvelles_paires = json.loads(texte)

            prochain_id = len(dataset) + 1
            for paire in nouvelles_paires:
                paire["id"] = str(prochain_id).zfill(5)
                dataset.append(paire)
                prochain_id += 1

            print(f" ✅ {len(nouvelles_paires)} paires ajoutées → Total : {len(dataset)}")
            erreurs_consecutives = 0
            index_theme += 1

            # Sauvegarde
            with open(chemin_dataset, "w", encoding="utf-8") as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)

            # Pause pour respecter le quota (4 sec entre chaque appel)
            time.sleep(4)

        except Exception as e:
            erreur = str(e)
            erreurs_consecutives += 1

            if "API_KEY_INVALID" in erreur or "expired" in erreur:
                print("[STOP] Clé API invalide. Crée une nouvelle clé sur aistudio.google.com")
                break

            elif "429" in erreur:
                # Extraire le délai suggéré
                import re
                match = re.search(r'retry in (\d+)', erreur)
                attente = int(match.group(1)) + 5 if match else 60
                print(f" ⏳ Quota dépassé. Pause de {attente} secondes...")
                time.sleep(attente)

            elif erreurs_consecutives >= 5:
                print("[STOP] Trop d'erreurs consécutives. Arrêt.")
                break
            else:
                print(f" ⚠️ Erreur : {erreur[:100]}. Retry dans 5s...")
                time.sleep(5)

    print(f"\n🎉 TOTAL FINAL : {len(dataset)} paires")

except KeyboardInterrupt:
    print(f"\n[STOP] Interrompu. Total sauvegardé : {len(dataset)} paires")
