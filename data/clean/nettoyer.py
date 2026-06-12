import json

# Charger le dataset brut
with open("data/raw/data_collectee.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Avant nettoyage : {len(data)} entrées")

# ─────────────────────────────────────────
# 1. SUPPRIMER LES ENTRÉES INUTILES
# ─────────────────────────────────────────
mots_a_exclure = [
    "cookie", "cookies", "données personnelles",
    "navigation", "actualités récentes", "agenda",
    "consentez", "accepter"
]

def est_utile(item):
    question = item["question"].lower()
    reponse = item["reponse"].lower()
    for mot in mots_a_exclure:
        if mot in question or mot in reponse:
            return False
    # Supprimer les réponses trop courtes
    if len(item["reponse"]) < 50:
        return False
    return True

data_propre = [item for item in data if est_utile(item)]
print(f"Après suppression inutiles : {len(data_propre)} entrées")

# ─────────────────────────────────────────
# 2. SUPPRIMER LES DOUBLONS
# ─────────────────────────────────────────
vus = set()
data_unique = []

for item in data_propre:
    cle = item["question"].strip().lower()
    if cle not in vus:
        vus.add(cle)
        data_unique.append(item)

print(f"Après suppression doublons : {len(data_unique)} entrées")

# ─────────────────────────────────────────
# 3. AMÉLIORER LA CATÉGORISATION
# ─────────────────────────────────────────
def categoriser(item):
    texte = (item["question"] + " " + item["reponse"]).lower()
    
    if any(m in texte for m in ["bac", "باكالوريا", "examen", "امتحان"]):
        return "examens"
    elif any(m in texte for m in ["inscription", "تسجيل", "concours", "مباراة"]):
        return "inscription"
    elif any(m in texte for m in ["université", "جامعة", "licence", "master"]):
        return "université"
    elif any(m in texte for m in ["orientation", "توجيه", "filière", "شعبة"]):
        return "orientation"
    elif any(m in texte for m in ["massar", "مسار", "plateforme", "منصة"]):
        return "numérique"
    else:
        return "général"

def niveau_auto(item):
    texte = (item["question"] + " " + item["reponse"]).lower()
    if any(m in texte for m in ["bac", "باكالوريا", "lycée", "ثانوي تأهيلي"]):
        return "bac"
    elif any(m in texte for m in ["université", "جامعة", "licence", "master", "doctorat"]):
        return "université"
    elif any(m in texte for m in ["collège", "إعدادي", "collégial"]):
        return "collège"
    elif any(m in texte for m in ["primaire", "ابتدائي"]):
        return "primaire"
    else:
        return "général"

for item in data_unique:
    item["categorie"] = categoriser(item)
    item["niveau"] = niveau_auto(item)

# ─────────────────────────────────────────
# 4. RÉINDEXER LES IDs
# ─────────────────────────────────────────
for i, item in enumerate(data_unique):
    item["id"] = str(i + 1).zfill(4)

# ─────────────────────────────────────────
# 5. SAUVEGARDER
# ─────────────────────────────────────────
import os
os.makedirs("data/clean", exist_ok=True)

with open("data/clean/dataset_propre.json", "w", encoding="utf-8") as f:
    json.dump(data_unique, f, ensure_ascii=False, indent=4)

# ─────────────────────────────────────────
# RÉSUMÉ FINAL
# ─────────────────────────────────────────
print(f"\n{'='*50}")
print(f"✅ Nettoyage terminé !")
print(f"📊 Entrées finales : {len(data_unique)}")
print(f"📁 Sauvegardé : data/clean/dataset_propre.json")
print(f"\n📋 Par catégorie :")

categories = {}
for item in data_unique:
    cat = item["categorie"]
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items()):
    print(f"   {cat} : {count} entrées")