# scripts/extraire_questions.py
import json

with open("data/final/dataset_final.json", "r", encoding="utf-8") as f:
    data = json.load(f)

questions = [item["question"] for item in data]

with open("data/questions_existantes.txt", "w", encoding="utf-8") as f:
    for q in questions:
        f.write(q + "\n")

print(f"✅ {len(questions)} questions exportées")