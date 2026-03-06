import json
import difflib

def load_knowledge_base():
    with open("knowledge_base.json", "r", encoding="utf-8") as file:
        return json.load(file)

knowledge_base = load_knowledge_base()


def ask_ai(message: str):

    message = message.lower()
    best_match = None
    highest_score = 0

    for topic in knowledge_base.values():
        for keyword in topic["keywords"]:
            score = difflib.SequenceMatcher(None, keyword, message).ratio()
            if score > highest_score:
                highest_score = score
                best_match = topic

    if best_match and highest_score > 0.3:
        return best_match["response"], best_match["department"]

    return (
        "Su consulta fue derivada al área general para revisión manual.",
        "General"
    )
