"""doctor management extensions

Revision ID: 20260720_0004
Revises: 20260720_0003
Create Date: 2026-07-20
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
revision="20260720_0004"; down_revision="20260720_0003"; branch_labels=None; depends_on=None

def base_columns(): return [sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)]
def org_hcp(): return [sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("hcp_id", postgresql.UUID(as_uuid=True), nullable=False)]
def common(table):
    op.create_foreign_key(f"fk_{table}_organization_id_organizations", table, "organizations", ["organization_id"], ["id"], ondelete="CASCADE"); op.create_foreign_key(f"fk_{table}_hcp_id_hcps", table, "hcps", ["hcp_id"], ["id"], ondelete="CASCADE"); op.create_index(f"ix_{table}_organization_id", table, ["organization_id"]); op.create_index(f"ix_{table}_hcp_id", table, ["hcp_id"]); op.create_index(f"ix_{table}_deleted_at", table, ["deleted_at"])
def upgrade():
    op.add_column("hcps", sa.Column("status", sa.String(40), server_default="active", nullable=False)); op.create_index("ix_hcps_status", "hcps", ["status"])
    op.create_table("doctor_tags", *base_columns(), *org_hcp(), sa.Column("name",sa.String(80),nullable=False), sa.Column("color",sa.String(20)), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("organization_id","hcp_id","name", name="uq_doctor_tags_org_hcp_name")); common("doctor_tags")
    op.create_table("doctor_product_associations", *base_columns(), *org_hcp(), sa.Column("product_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("relationship_type",sa.String(60),nullable=False), sa.Column("strength",sa.Float(),nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("organization_id","hcp_id","product_id", name="uq_doctor_products_org_hcp_product")); common("doctor_product_associations"); op.create_foreign_key("fk_doctor_products_product_id_products", "doctor_product_associations", "products", ["product_id"], ["id"], ondelete="CASCADE")
    op.create_table("doctor_campaign_associations", *base_columns(), *org_hcp(), sa.Column("campaign_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("status",sa.String(60),nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("organization_id","hcp_id","campaign_id", name="uq_doctor_campaigns_org_hcp_campaign")); common("doctor_campaign_associations"); op.create_foreign_key("fk_doctor_campaigns_campaign_id_campaigns", "doctor_campaign_associations", "campaigns", ["campaign_id"], ["id"], ondelete="CASCADE")
    op.create_table("doctor_priority_snapshots", *base_columns(), *org_hcp(), sa.Column("total_score",sa.Float(),nullable=False), sa.Column("classification",sa.String(40),nullable=False), sa.Column("factors",postgresql.JSONB(),nullable=False), sa.Column("explanation",sa.Text(),nullable=False), sa.PrimaryKeyConstraint("id")); common("doctor_priority_snapshots"); op.create_index("ix_doctor_priority_snapshots_classification", "doctor_priority_snapshots", ["classification"])
def downgrade():
    for t in ["doctor_priority_snapshots","doctor_campaign_associations","doctor_product_associations","doctor_tags"]: op.drop_table(t)
    op.drop_index("ix_hcps_status", table_name="hcps"); op.drop_column("hcps", "status")
