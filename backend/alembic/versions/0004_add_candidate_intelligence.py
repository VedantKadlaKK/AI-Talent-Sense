"""add candidate intelligence

Revision ID: 0004_add_candidate_intelligence
Revises: 0003_create_candidates
Create Date: 2026-07-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_add_candidate_intelligence"
down_revision = "0003_create_candidates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("candidate_profiles", sa.Column("normalized_summary", sa.Text(), nullable=True))
    op.add_column("candidate_profiles", sa.Column("source_coverage", sa.JSON(), nullable=True))
    op.add_column("candidate_profiles", sa.Column("resume_insights", sa.JSON(), nullable=True))
    op.add_column("candidate_profiles", sa.Column("github_insights", sa.JSON(), nullable=True))
    op.add_column("candidate_profiles", sa.Column("portfolio_insights", sa.JSON(), nullable=True))
    op.add_column("candidate_profiles", sa.Column("api_insights", sa.JSON(), nullable=True))
    op.add_column("candidate_profiles", sa.Column("normalized_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("candidate_profiles", "normalized_at")
    op.drop_column("candidate_profiles", "api_insights")
    op.drop_column("candidate_profiles", "portfolio_insights")
    op.drop_column("candidate_profiles", "github_insights")
    op.drop_column("candidate_profiles", "resume_insights")
    op.drop_column("candidate_profiles", "source_coverage")
    op.drop_column("candidate_profiles", "normalized_summary")
