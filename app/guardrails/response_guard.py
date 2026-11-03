
import re

SENSITIVE_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?(system|hidden)\s+prompt",
    r"show\s+(me\s+)?your\s+system\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
]


def check_response(answer: str, context: str) -> dict:
    """Check an AI response for basic safety and support issues."""

    if not answer or not answer.strip():
        return {
            "safe": False,
            "issues": ["Empty response"],
        }

    issues = []

    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, answer, re.IGNORECASE):
            issues.append("Potential instruction disclosure or injection content")
            break

    answer_numbers = set(
        re.findall(r"\b\d+(?:\.\d+)?\b", answer)
    )
    context_numbers = set(
        re.findall(r"\b\d+(?:\.\d+)?\b", context)
    )

    unsupported_numbers = answer_numbers - context_numbers

    if unsupported_numbers:
        issues.append("Unsupported numerical claims detected")

    return {
        "safe": len(issues) == 0,
        "issues": issues,
    }
