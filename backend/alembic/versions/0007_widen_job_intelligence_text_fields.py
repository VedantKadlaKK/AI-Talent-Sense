"""widen job intelligence text fields

Revision ID: 0007_widen_job_intel_text
Revises: 0006_create_recommendations
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_widen_job_intel_text"
down_revision = "0006_create_recommendations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "job_intelligence",
        "experience",
        existing_type=sa.String(length=160),
        type_=sa.Text(),
        existing_nullable=False,
    )
    op.alter_column(
        "job_intelligence",
        "education",
        existing_type=sa.String(length=240),
        type_=sa.Text(),
        existing_nullable=False,
    )
    op.alter_column(
        "job_intelligence",
        "industry",
        existing_type=sa.String(length=160),
        type_=sa.Text(),
        existing_nullable=False,
    )
    op.alter_column(
        "job_intelligence",
        "location",
        existing_type=sa.String(length=160),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "job_intelligence",
        "location",
        existing_type=sa.Text(),
        type_=sa.String(length=160),
        existing_nullable=False,
    )
    op.alter_column(
        "job_intelligence",
        "industry",
        existing_type=sa.Text(),
        type_=sa.String(length=160),
        existing_nullable=False,
    )
    op.alter_column(
        "job_intelligence",
        "education",
        existing_type=sa.Text(),
        type_=sa.String(length=240),
        existing_nullable=False,
    )
    op.alter_column(
        "job_intelligence",
        "experience",
        existing_type=sa.Text(),
        type_=sa.String(length=160),
        existing_nullable=False,
    )
