from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from api.models.signal import Signal, SignalResult


class SignalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_enabled(self) -> list[Signal]:
        statement = select(Signal).where(Signal.enabled.is_(True)).order_by(Signal.id.asc())
        return list(self.db.scalars(statement).all())

    def list_results_for_job(self, job_id: int) -> list[SignalResult]:
        statement = (
            select(SignalResult)
            .options(selectinload(SignalResult.signal))
            .where(SignalResult.job_id == job_id)
            .order_by(SignalResult.candidate_id.asc(), SignalResult.id.asc())
        )
        return list(self.db.scalars(statement).all())

    def ensure_defaults(self, definitions: list[dict[str, object]]) -> list[Signal]:
        for definition in definitions:
            name = str(definition["name"])
            signal = self._get_by_name(name)
            values = {
                "category": str(definition["category"]),
                "description": str(definition["description"]),
                "default_weight": float(definition["default_weight"]),
                "enabled": bool(definition.get("enabled", True)),
            }
            if signal is None:
                self.db.add(Signal(name=name, **values))
            else:
                for key, value in values.items():
                    setattr(signal, key, value)
        self.db.commit()
        return self.list_enabled()

    def upsert_result(
        self,
        candidate_id: int,
        job_id: int,
        signal_id: int,
        score: float,
        weight: float,
        reason: str,
    ) -> SignalResult:
        statement = select(SignalResult).where(
            SignalResult.candidate_id == candidate_id,
            SignalResult.job_id == job_id,
            SignalResult.signal_id == signal_id,
        )
        result = self.db.scalars(statement).one_or_none()
        contribution = score * weight
        if result is None:
            result = SignalResult(
                candidate_id=candidate_id,
                job_id=job_id,
                signal_id=signal_id,
                score=score,
                weight=weight,
                contribution=contribution,
                reason=reason,
            )
            self.db.add(result)
        else:
            result.score = score
            result.weight = weight
            result.contribution = contribution
            result.reason = reason
        self.db.commit()
        self.db.refresh(result)
        return result

    def _get_by_name(self, name: str) -> Signal | None:
        statement = select(Signal).where(Signal.name == name)
        return self.db.scalars(statement).one_or_none()
