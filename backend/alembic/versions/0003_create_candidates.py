"""create candidates

Revision ID: 0003_create_candidates
Revises: 0002_create_job_intelligence
Create Date: 2026-07-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_create_candidates"
down_revision = "0002_create_job_intelligence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=240), nullable=False),
        sa.Column("phone", sa.String(length=80), nullable=False),
        sa.Column("location", sa.String(length=160), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("experience", sa.String(length=160), nullable=False),
        sa.Column("current_company", sa.String(length=160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_candidates_email"), "candidates", ["email"], unique=True)
    op.create_index(op.f("ix_candidates_full_name"), "candidates", ["full_name"], unique=False)
    op.create_index(op.f("ix_candidates_id"), "candidates", ["id"], unique=False)

    op.create_table(
        "candidate_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("external_id", sa.String(length=160), nullable=False),
        sa.Column("profile_url", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source", "external_id", name="uq_candidate_source_external_id"),
    )
    op.create_index(op.f("ix_candidate_sources_id"), "candidate_sources", ["id"], unique=False)
    op.create_index(op.f("ix_candidate_sources_source"), "candidate_sources", ["source"], unique=False)

    op.create_table(
        "candidate_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("projects", sa.JSON(), nullable=False),
        sa.Column("education", sa.JSON(), nullable=False),
        sa.Column("certifications", sa.JSON(), nullable=False),
        sa.Column("github_username", sa.String(length=120), nullable=False),
        sa.Column("portfolio_url", sa.String(length=500), nullable=False),
        sa.Column("resume_path", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id"),
    )
    op.create_index(op.f("ix_candidate_profiles_id"), "candidate_profiles", ["id"], unique=False)

    op.create_table(
        "job_candidates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("match_reasons", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", "candidate_id", name="uq_job_candidate"),
    )
    op.create_index(op.f("ix_job_candidates_id"), "job_candidates", ["id"], unique=False)
    op.create_index(op.f("ix_job_candidates_job_id"), "job_candidates", ["job_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_job_candidates_job_id"), table_name="job_candidates")
    op.drop_index(op.f("ix_job_candidates_id"), table_name="job_candidates")
    op.drop_table("job_candidates")
    op.drop_index(op.f("ix_candidate_profiles_id"), table_name="candidate_profiles")
    op.drop_table("candidate_profiles")
    op.drop_index(op.f("ix_candidate_sources_source"), table_name="candidate_sources")
    op.drop_index(op.f("ix_candidate_sources_id"), table_name="candidate_sources")
    op.drop_table("candidate_sources")
    op.drop_index(op.f("ix_candidates_id"), table_name="candidates")
    op.drop_index(op.f("ix_candidates_full_name"), table_name="candidates")
    op.drop_index(op.f("ix_candidates_email"), table_name="candidates")
    op.drop_table("candidates")
