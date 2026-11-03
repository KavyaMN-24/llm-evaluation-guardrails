
import re
from typing import Any

REFUSAL_PHRASES = (
    "i cannot",
    "i can't",
    "not available in the provided context",
    "cannot provide",
    "cannot reveal",
    "i don't have enough information",
)

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were",
    "to", "of", "in", "on", "and", "or", "for",
    "with", "within", "from", "it", "this", "that",
    "can", "be", "only", "currently", "i", "not",
    "does", "do", "have", "has", "all", "may",
}


def tokenize(text: str) -> set[str]:
    """Convert text into a set of meaningful lowercase words."""
    words = re.findall(r"\b[a-z0-9]+\b", text.lower())
    return {word for word in words if word not in STOPWORDS}


def calculate_similarity(expected: str, actual: str) -> float:
    """Calculate token-based F1 similarity."""
    expected_tokens = tokenize(expected)
    actual_tokens = tokenize(actual)

    if not expected_tokens and not actual_tokens:
        return 1.0

    if not expected_tokens or not actual_tokens:
        return 0.0

    overlap = expected_tokens & actual_tokens

    precision = len(overlap) / len(actual_tokens)
    recall = len(overlap) / len(expected_tokens)

    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


def calculate_groundedness(answer: str, context: str) -> float:
    """Estimate support and detect unsupported numeric claims."""
    answer_tokens = tokenize(answer)
    context_tokens = tokenize(context)

    if not answer_tokens:
        return 0.0

    answer_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", answer))
    context_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", context))

    # Penalize numerical claims absent from the source context.
    if answer_numbers - context_numbers:
        return 0.0

    supported = answer_tokens & context_tokens
    return len(supported) / len(answer_tokens)

def detect_refusal(answer: str) -> bool:
    """Detect common refusal phrases."""
    normalized = answer.lower()
    return any(phrase in normalized for phrase in REFUSAL_PHRASES)


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one AI response against its reference and context."""
    answer = case["model_answer"]
    expected = case["expected_answer"]
    context = case["context"]
    should_refuse = case["should_refuse"]

    refusal_detected = detect_refusal(answer)

    relevance = calculate_similarity(expected, answer)

    if should_refuse and refusal_detected:
        groundedness = 1.0
    else:
        groundedness = calculate_groundedness(answer, context)

    refusal_compliance = float(
        refusal_detected == should_refuse
    )

    overall_score = (
        relevance + groundedness + refusal_compliance
    ) / 3

    return {
        "id": case["id"],
        "relevance": round(relevance, 3),
        "groundedness": round(groundedness, 3),
        "refusal_compliance": round(refusal_compliance, 3),
        "overall_score": round(overall_score, 3),
        "passed": (
            relevance >= 0.5
            and groundedness >= 0.5
            and refusal_compliance == 1.0
        ),
    }


def evaluate_dataset(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate all cases and calculate aggregate metrics."""
    if not cases:
        raise ValueError("Evaluation dataset cannot be empty.")

    results = [evaluate_case(case) for case in cases]

    count = len(results)

    return {
        "total_cases": count,
        "passed_cases": sum(result["passed"] for result in results),
        "failed_cases": sum(not result["passed"] for result in results),
        "pass_rate": round(
            sum(result["passed"] for result in results) / count, 3
        ),
        "average_relevance": round(
            sum(result["relevance"] for result in results) / count, 3
        ),
        "average_groundedness": round(
            sum(result["groundedness"] for result in results) / count, 3
        ),
        "average_refusal_compliance": round(
            sum(result["refusal_compliance"] for result in results) / count, 3
        ),
        "average_score": round(
            sum(result["overall_score"] for result in results) / count, 3
        ),
        "results": results,
    }
