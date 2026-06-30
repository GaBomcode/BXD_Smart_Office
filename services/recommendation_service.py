"""Recommendation service for Advisory Report Engine."""

from __future__ import annotations

from collections import defaultdict
import logging

from models.report_evidence import ReportEvidence
from models.report_recommendation import ReportRecommendation

logger = logging.getLogger(__name__)


class RecommendationService:
    """Score, deduplicate, rank and group advisory recommendations."""

    def build_recommendations(self, evidence: list[ReportEvidence]) -> list[ReportRecommendation]:
        """Build deterministic recommendations from evidence."""
        logger.info("Build recommendations from %s evidence items", len(evidence))
        recommendations: list[ReportRecommendation] = []
        task_evidence = [item for item in evidence if item.source_type == "task"]
        for item in task_evidence:
            status = str(item.metadata.get("status") or "")
            progress = int(item.metadata.get("progress") or 0)
            task_id = int(item.source_id)
            if progress < 100 and status != "Hoan thanh":
                recommendations.append(
                    ReportRecommendation(
                        title=f"Follow up task #{task_id}",
                        reason="Task is not completed and has traceable task evidence.",
                        supporting_evidence=[item],
                        confidence_score=self.score_recommendation([item]),
                        affected_tasks=[task_id],
                        priority=self._priority(item),
                    )
                )
        return self.rank(self.remove_duplicates(recommendations))

    def score_recommendation(self, evidence: list[ReportEvidence]) -> float:
        """Score one recommendation by evidence confidence."""
        if not evidence:
            return 0.0
        score = sum(item.confidence for item in evidence) / len(evidence)
        return round(min(score, 1.0), 4)

    def remove_duplicates(
        self,
        recommendations: list[ReportRecommendation],
    ) -> list[ReportRecommendation]:
        """Remove duplicate recommendations by title and affected tasks."""
        seen: set[tuple[str, tuple[int, ...]]] = set()
        unique: list[ReportRecommendation] = []
        for item in recommendations:
            key = (item.title.lower(), tuple(sorted(item.affected_tasks)))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique

    def rank(self, recommendations: list[ReportRecommendation]) -> list[ReportRecommendation]:
        """Rank recommendations by priority and confidence."""
        priority_weight = {"high": 3, "medium": 2, "low": 1}
        return sorted(
            recommendations,
            key=lambda item: (priority_weight.get(item.priority, 0), item.confidence_score),
            reverse=True,
        )

    def group(self, recommendations: list[ReportRecommendation]) -> dict[str, list[ReportRecommendation]]:
        """Group recommendations by priority."""
        grouped: dict[str, list[ReportRecommendation]] = defaultdict(list)
        for item in recommendations:
            grouped[item.priority].append(item)
        return dict(grouped)

    @staticmethod
    def _priority(evidence: ReportEvidence) -> str:
        priority = str(evidence.metadata.get("priority") or "").lower()
        progress = int(evidence.metadata.get("progress") or 0)
        if "cao" in priority or progress < 30:
            return "high"
        if progress < 70:
            return "medium"
        return "low"
