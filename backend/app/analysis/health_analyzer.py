"""Health score — documented, non-arbitrary penalties."""

from __future__ import annotations

from app.models.analysis_result import HealthScore, ScorePenalty
from app.models.finding import Finding, FindingConfidence, FindingSeverity

# Documented caps / amounts (ARCHITECTURE.md + README)
_PENALTIES = {
    ("dependency", FindingSeverity.CRITICAL, FindingConfidence.CONFIRMED): (15, 5),  # amount, cap count
    ("conflict", FindingSeverity.CRITICAL, FindingConfidence.CONFIRMED): (10, 10),
    ("version", FindingSeverity.CRITICAL, FindingConfidence.CONFIRMED): (8, 10),
    ("duplicate", FindingSeverity.WARNING, FindingConfidence.CONFIRMED): (5, 10),
    ("environment", FindingSeverity.WARNING, FindingConfidence.CONFIRMED): (4, 10),
    ("environment", FindingSeverity.WARNING, FindingConfidence.POTENTIAL): (2, 10),
    ("conflict", FindingSeverity.WARNING, FindingConfidence.POTENTIAL): (2, 10),
    ("compatibility", FindingSeverity.WARNING, FindingConfidence.POTENTIAL): (2, 10),
    ("parse", FindingSeverity.WARNING, FindingConfidence.CONFIRMED): (1, 20),
}


def compute_health_score(findings: list[Finding]) -> HealthScore:
    """Start at 100; subtract documented penalties; clamp 0–100."""
    score = 100
    explanation: list[ScorePenalty] = []
    category_deductions: dict[str, int] = {}
    applied_counts: dict[tuple, int] = {}

    # Sort for stable explanation order: critical first
    severity_order = {
        FindingSeverity.CRITICAL: 0,
        FindingSeverity.WARNING: 1,
        FindingSeverity.INFO: 2,
    }
    ordered = sorted(findings, key=lambda f: (severity_order.get(f.severity, 9), f.category, f.title))

    for finding in ordered:
        key = (finding.category, finding.severity, finding.confidence)
        # Also try looser matches for duplicate multi-version etc.
        rule = _PENALTIES.get(key)
        if rule is None and finding.category == "duplicate":
            rule = _PENALTIES.get(("duplicate", FindingSeverity.WARNING, FindingConfidence.CONFIRMED))
        if rule is None and finding.severity == FindingSeverity.INFO:
            continue  # informational: 0
        if rule is None and finding.confidence == FindingConfidence.POTENTIAL:
            # Generic potential conflict-ish
            amount, cap = 2, 10
        elif rule is None:
            continue
        else:
            amount, cap = rule

        count = applied_counts.get(key, 0)
        if count >= cap:
            continue
        applied_counts[key] = count + 1

        score -= amount
        category_deductions[finding.category] = category_deductions.get(finding.category, 0) + amount
        explanation.append(
            ScorePenalty(
                reason=finding.title,
                amount=amount,
                category=finding.category,
                finding_id=finding.id,
            )
        )

    score = max(0, min(100, score))
    category_scores = {
        cat: max(0, 100 - deducted) for cat, deducted in category_deductions.items()
    }
    # Ensure empty categories still make sense for UI
    if not category_scores:
        category_scores = {"overall": score}

    return HealthScore(score=score, category_scores=category_scores, score_explanation=explanation)
