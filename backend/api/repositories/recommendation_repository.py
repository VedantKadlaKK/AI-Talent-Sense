from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.recommendation import Recommendation


class RecommendationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_job(self, job_id: int) -> list[Recommendation]:
        statement = (
            select(Recommendation)
            .where(Recommendation.job_id == job_id)
            .order_by(Recommendation.rank.asc(), Recommendation.overall_score.desc())
        )
        return list(self.db.scalars(statement).all())

    def upsert(
        self,
        candidate_id: int,
        job_id: int,
        overall_score: float,
        rank: int,
        summary: str,
        strengths: list[str],
        weaknesses: list[str],
        missing_skills: list[str],
        recommendation: str,
        raw_ai_output: dict[str, object],
    ) -> Recommendation:
        statement = select(Recommendation).where(
            Recommendation.candidate_id == candidate_id,
            Recommendation.job_id == job_id,
        )
        item = self.db.scalars(statement).one_or_none()
        values = {
            "overall_score": overall_score,
            "rank": rank,
            "summary": summary,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "missing_skills": missing_skills,
            "recommendation": recommendation,
            "raw_ai_output": raw_ai_output,
        }
        if item is None:
            item = Recommendation(candidate_id=candidate_id, job_id=job_id, **values)
            self.db.add(item)
        else:
            for key, value in values.items():
                setattr(item, key, value)

        self.db.commit()
        self.db.refresh(item)
        return item
