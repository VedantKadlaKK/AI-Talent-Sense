"""widen recommendation text

Revision ID: 0008_reco_text
Revises: 0007_widen_job_intel_text
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_reco_text"
down_revision = "0007_widen_job_intel_text"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "recommendations",
        "recommendation",
        existing_type=sa.String(length=80),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "recommendations",
        "recommendation",
        existing_type=sa.Text(),
        type_=sa.String(length=80),
        existing_nullable=False,
    )
