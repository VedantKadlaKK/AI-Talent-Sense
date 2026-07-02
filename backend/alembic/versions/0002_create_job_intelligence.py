"""create job intelligence

Revision ID: 0002_create_job_intelligence
Revises: 0001_create_jobs
Create Date: 2026-07-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_create_job_intelligence"
down_revision = "0001_create_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_intelligence",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("experience", sa.String(length=160), nullable=False),
        sa.Column("education", sa.String(length=240), nullable=False),
        sa.Column("industry", sa.String(length=160), nullable=False),
        sa.Column("location", sa.String(length=160), nullable=False),
        sa.Column("seniority", sa.String(length=120), nullable=False),
        sa.Column("certifications", sa.JSON(), nullable=False),
        sa.Column("nice_to_have_skills", sa.JSON(), nullable=False),
        sa.Column("raw_ai_output", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
    )
    op.create_index(op.f("ix_job_intelligence_id"), "job_intelligence", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_job_intelligence_id"), table_name="job_intelligence")
    op.drop_table("job_intelligence")
