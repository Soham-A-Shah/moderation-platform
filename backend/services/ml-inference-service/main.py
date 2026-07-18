from moderation_common.events import consume_forever


def calculate_scores(text):
    text = text.lower()

    toxicity_terms = ["hate", "abuse", "harass"]
    spam_terms = ["spam", "scam", "free money", "buy now"]
    violence_terms = ["kill", "attack", "violence"]

    return {
        "toxicity": min(0.99, 0.08 + 0.30 * sum(term in text for term in toxicity_terms)),
        "spam": min(0.99, 0.04 + 0.30 * sum(term in text for term in spam_terms)),
        "violence": min(0.99, 0.03 + 0.35 * sum(term in text for term in violence_terms)),
    }


def handle(event, producer):
    scores = {
        key: round(value, 2)
        for key, value in calculate_scores(event.get("normalized_text", "")).items()
    }

    event["scores"] = scores
    event["model_version"] = "mock-moderation-v1"

    producer.publish("ml.scored", "ML_SCORED", event)


if __name__ == "__main__":
    consume_forever("ml-inference-service", "content.normalized", handle)
