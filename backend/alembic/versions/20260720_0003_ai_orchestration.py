"""ai orchestration schema

Revision ID: 20260720_0003
Revises: 20260720_0002
Create Date: 2026-07-20
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
revision = "20260720_0003"
down_revision = "20260720_0002"
branch_labels = None
depends_on = None

def base_columns():
    return [sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)]

def org_user_cols():
    return [sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False)]

def common_fks(table):
    op.create_foreign_key(f"fk_{table}_organization_id_organizations", table, "organizations", ["organization_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key(f"fk_{table}_user_id_users", table, "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_index(f"ix_{table}_organization_id", table, ["organization_id"]); op.create_index(f"ix_{table}_user_id", table, ["user_id"]); op.create_index(f"ix_{table}_deleted_at", table, ["deleted_at"])

def upgrade():
    op.create_table("ai_conversations", *base_columns(), *org_user_cols(), sa.Column("title", sa.String(200), nullable=False), sa.Column("summary", sa.Text()), sa.Column("metadata", postgresql.JSONB(), nullable=False), sa.PrimaryKeyConstraint("id")); common_fks("ai_conversations")
    op.create_table("ai_conversation_messages", *base_columns(), sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("role", sa.String(20), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("metadata", postgresql.JSONB(), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_foreign_key("fk_ai_conversation_messages_organization_id_organizations", "ai_conversation_messages", "organizations", ["organization_id"], ["id"], ondelete="CASCADE"); op.create_foreign_key("fk_ai_conversation_messages_conversation_id_ai_conversations", "ai_conversation_messages", "ai_conversations", ["conversation_id"], ["id"], ondelete="CASCADE"); op.create_index("ix_ai_conversation_messages_conversation_id", "ai_conversation_messages", ["conversation_id"]); op.create_index("ix_ai_conversation_messages_organization_id", "ai_conversation_messages", ["organization_id"]); op.create_index("ix_ai_conversation_messages_deleted_at", "ai_conversation_messages", ["deleted_at"])
    op.create_table("ai_memories", *base_columns(), *org_user_cols(), sa.Column("conversation_id", postgresql.UUID(as_uuid=True)), sa.Column("memory_type", sa.String(40), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.PrimaryKeyConstraint("id")); common_fks("ai_memories"); op.create_foreign_key("fk_ai_memories_conversation_id_ai_conversations", "ai_memories", "ai_conversations", ["conversation_id"], ["id"], ondelete="CASCADE")
    op.create_table("ai_execution_logs", *base_columns(), *org_user_cols(), sa.Column("trace_id", sa.String(80), nullable=False), sa.Column("graph_node", sa.String(120), nullable=False), sa.Column("latency_ms", sa.Integer(), nullable=False), sa.Column("prompt_tokens", sa.Integer(), nullable=False), sa.Column("completion_tokens", sa.Integer(), nullable=False), sa.Column("estimated_cost_usd", sa.Float(), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("metadata", postgresql.JSONB(), nullable=False), sa.PrimaryKeyConstraint("id")); common_fks("ai_execution_logs"); op.create_index("ix_ai_execution_logs_trace_id", "ai_execution_logs", ["trace_id"])

def downgrade():
    for table in ["ai_execution_logs", "ai_memories", "ai_conversation_messages", "ai_conversations"]: op.drop_table(table)
