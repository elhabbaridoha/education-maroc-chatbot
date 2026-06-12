# scripts/fusionner.py
import json, glob, os

# 1. Charger le dataset existant (scraping)
with open("data/clean/dataset_propre.json", "r", encoding="utf-8") as f:
    dataset_final = json.load(f)

print(f"Dataset existant : {len(dataset_final)} paires")

# 2. Charger tous les blocs générés
blocs = sorted(glob.glob("data/generated/bloc_*.json"))
print(f"Blocs trouvés : {len(blocs)}")

for fichier in blocs:
    with open(fichier, "r", encoding="utf-8") as f:
        paires = json.load(f)
        dataset_final.extend(paires)
    print(f"  ✅ {fichier} → {len(paires)} paires")

# 3. Réindexer les IDs
for i, item in enumerate(dataset_final):
    item["id"] = str(i + 1).zfill(5)

# 4. Sauvegarder le fichier final
os.makedirs("data/final", exist_ok=True)
with open("data/final/dataset_final.json", "w", encoding="utf-8") as f:
    json.dump(dataset_final, f, ensure_ascii=False, indent=2)

print(f"\n🎉 TOTAL FINAL : {len(dataset_final)} paires")
print(f"📁 Sauvegardé : data/final/dataset_final.json")