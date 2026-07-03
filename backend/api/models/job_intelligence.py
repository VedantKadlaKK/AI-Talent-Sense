from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base


class JobIntelligence(Base):
    __tablename__ = "job_intelligence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, nullable=False)
    skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    experience: Mapped[str] = mapped_column(Text, nullable=False, default="")
    education: Mapped[str] = mapped_column(Text, nullable=False, default="")
    industry: Mapped[str] = mapped_column(Text, nullable=False, default="")
    location: Mapped[str] = mapped_column(Text, nullable=False, default="")
    seniority: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    certifications: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    nice_to_have_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    raw_ai_output: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
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

    job: Mapped["Job"] = relationship("Job", back_populates="intelligence")
