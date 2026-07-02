from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(240), nullable=False, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    location: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    experience: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    current_company: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    sources: Mapped[list["CandidateSource"]] = relationship(
        "CandidateSource",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    profile: Mapped["CandidateProfile | None"] = relationship(
        "CandidateProfile",
        back_populates="candidate",
        cascade="all, delete-orphan",
        uselist=False,
    )
    job_matches: Mapped[list["JobCandidate"]] = relationship(
        "JobCandidate",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    signal_results: Mapped[list["SignalResult"]] = relationship(
        "SignalResult",
        cascade="all, delete-orphan",
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        cascade="all, delete-orphan",
    )


class CandidateSource(Base):
    __tablename__ = "candidate_sources"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_candidate_source_external_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(160), nullable=False)
    profile_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="sources")


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    projects: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    education: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    certifications: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    github_username: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    portfolio_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    resume_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    normalized_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_coverage: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    resume_insights: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    github_insights: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    portfolio_insights: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    api_insights: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    normalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="profile")


class JobCandidate(Base):
    __tablename__ = "job_candidates"
    __table_args__ = (UniqueConstraint("job_id", "candidate_id", name="uq_job_candidate"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(String(80), nullable=False, default="mock")
    match_reasons: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="job_matches")
