import json

from difflib import SequenceMatcher


with open(
        "evaluation/golden_dataset.json"
) as f:

    dataset = json.load(f)

scores = []

for item in dataset:

    similarity = SequenceMatcher(

        None,

        item["question"].lower(),

        item["expected"].lower()

    ).ratio()

    scores.append(
        similarity
    )

avg = sum(scores) / len(scores)

print(
    "Evaluation Score:",
    round(avg, 2)
)