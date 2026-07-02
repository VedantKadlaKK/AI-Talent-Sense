"""create signals

Revision ID: 0005_create_signals
Revises: 0004_add_candidate_intelligence
Create Date: 2026-07-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_create_signals"
down_revision = "0004_add_candidate_intelligence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("default_weight", sa.Float(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_signals_category"), "signals", ["category"], unique=False)
    op.create_index(op.f("ix_signals_id"), "signals", ["id"], unique=False)
    op.create_index(op.f("ix_signals_name"), "signals", ["name"], unique=True)

    op.create_table(
        "signal_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("contribution", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("candidate_id", "job_id", "signal_id", name="uq_signal_result"),
    )
    op.create_index(op.f("ix_signal_results_id"), "signal_results", ["id"], unique=False)
    op.create_index(op.f("ix_signal_results_job_id"), "signal_results", ["job_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_signal_results_job_id"), table_name="signal_results")
    op.drop_index(op.f("ix_signal_results_id"), table_name="signal_results")
    op.drop_table("signal_results")
    op.drop_index(op.f("ix_signals_name"), table_name="signals")
    op.drop_index(op.f("ix_signals_id"), table_name="signals")
    op.drop_index(op.f("ix_signals_category"), table_name="signals")
    op.drop_table("signals")
