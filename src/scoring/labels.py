from src.config.settings import GOOD_THRESHOLD, MEDIUM_THRESHOLD


def label_from_score(score: float) -> str:
    if score >= GOOD_THRESHOLD:
        return "good"
    if score >= MEDIUM_THRESHOLD:
        return "medium"
    return "bad"
