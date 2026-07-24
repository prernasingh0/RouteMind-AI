"""initial identity schema

Revision ID: 20260720_0001
Revises: 
Create Date: 2026-07-20
"""
from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260720_0001"
down_revision = None
branch_labels = None
depends_on = None

def base_columns():
    return [sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)]

def upgrade() -> None:
    op.create_table("organizations", *base_columns(), sa.Column("name", sa.String(255), nullable=False), sa.Column("slug", sa.String(120), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("slug"))
    op.create_table("permissions", *base_columns(), sa.Column("code", sa.String(120), nullable=False), sa.Column("description", sa.Text()), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("code"))
    op.create_table("roles", *base_columns(), sa.Column("organization_id", postgresql.UUID(as_uuid=True)), sa.Column("name", sa.String(80), nullable=False), sa.Column("description", sa.Text()), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("organization_id", "name", name="uq_roles_org_name"))
    op.create_table("users", *base_columns(), sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("email", sa.String(320), nullable=False), sa.Column("hashed_password", sa.String(255), nullable=False), sa.Column("full_name", sa.String(255), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("is_superuser", sa.Boolean(), nullable=False), sa.Column("last_login_at", sa.DateTime(timezone=True)), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("organization_id", "email", name="uq_users_org_email"))
    op.create_table("role_permissions", sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("role_id", "permission_id"))
    op.create_table("user_roles", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("user_id", "role_id"))
    op.create_table("refresh_tokens", *base_columns(), sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("token_hash", sa.String(255), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("revoked_at", sa.DateTime(timezone=True)), sa.Column("user_agent", sa.String(255)), sa.Column("ip_address", postgresql.INET()), sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("token_hash"))
    op.create_table("audit_logs", *base_columns(), sa.Column("organization_id", postgresql.UUID(as_uuid=True)), sa.Column("actor_user_id", postgresql.UUID(as_uuid=True)), sa.Column("action", sa.String(120), nullable=False), sa.Column("resource_type", sa.String(120), nullable=False), sa.Column("resource_id", postgresql.UUID(as_uuid=True)), sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False), sa.Column("ip_address", postgresql.INET()), sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id"))
    for table in ["organizations","permissions","roles","users","refresh_tokens","audit_logs"]: op.create_index(f"ix_{table}_deleted_at", table, ["deleted_at"])
    op.create_index("ix_organizations_slug", "organizations", ["slug"]); op.create_index("ix_users_org_email", "users", ["organization_id","email"]); op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"]); op.create_index("ix_audit_logs_org_action_created", "audit_logs", ["organization_id","action","created_at"])

def downgrade() -> None:
    for table in ["audit_logs","refresh_tokens","user_roles","role_permissions","users","roles","permissions","organizations"]: op.drop_table(table)
