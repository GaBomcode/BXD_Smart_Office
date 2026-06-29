"""Human-readable AI Draft validation report builder."""

from __future__ import annotations


class ValidationReport:
    """Build plain-object reports for draft validation results."""

    @staticmethod
    def build(
        *,
        passed: bool,
        errors: list[str],
        warnings: list[str],
        score: float,
        recommendations: list[str],
    ) -> dict[str, object]:
        """Return a human-readable validation report."""
        if passed and warnings:
            status = "WARNING"
        elif passed:
            status = "PASS"
        else:
            status = "FAIL"
        return {
            "status": status,
            "summary": ValidationReport._summary(status, score, errors, warnings),
            "errors": errors,
            "warnings": warnings,
            "recommendations": recommendations,
        }

    @staticmethod
    def _summary(status: str, score: float, errors: list[str], warnings: list[str]) -> str:
        if status == "PASS":
            return f"PASS: Draft satisfies final validation with score {score:.2f}."
        if status == "WARNING":
            return f"WARNING: Draft can be exported, with {len(warnings)} warning(s)."
        return f"FAIL: Draft has {len(errors)} error(s) and cannot be exported."
