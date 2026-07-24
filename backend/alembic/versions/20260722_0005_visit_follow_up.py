"""add visit follow up scheduling

Revision ID: 20260722_0005
Revises: 20260720_0004
Create Date: 2026-07-22
"""
import sqlalchemy as sa
from alembic import op
revision = "20260722_0005"
down_revision = "20260720_0004"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("visits", sa.Column("follow_up_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_visits_follow_up_at", "visits", ["follow_up_at"])
def downgrade() -> None:
    op.drop_index("ix_visits_follow_up_at", table_name="visits")
    op.drop_column("visits", "follow_up_at")
