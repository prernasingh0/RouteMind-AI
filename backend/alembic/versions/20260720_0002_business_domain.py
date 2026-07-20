"""business domain schema

Revision ID: 20260720_0002
Revises: 20260720_0001
Create Date: 2026-07-20
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
revision = "20260720_0002"
down_revision = "20260720_0001"
branch_labels = None
depends_on = None

def base_columns():
    return [sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)]
def org_fk(): return sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False)
def fk(name, table, nullable=True, ondelete="SET NULL"): return sa.Column(name, postgresql.UUID(as_uuid=True), nullable=nullable)
def pk_fk_indexes(table):
    op.create_index(f"ix_{table}_organization_id", table, ["organization_id"]); op.create_index(f"ix_{table}_deleted_at", table, ["deleted_at"])

def upgrade():
    op.create_table("regions", *base_columns(), org_fk(), sa.Column("name", sa.String(160), nullable=False), sa.Column("code", sa.String(64)), sa.ForeignKeyConstraint(["organization_id"],["organizations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("organization_id","name", name="uq_regions_org_name")); pk_fk_indexes("regions")
    op.create_table("territories", *base_columns(), org_fk(), fk("region_id","regions"), sa.Column("name", sa.String(160), nullable=False), sa.Column("code", sa.String(64)), sa.Column("target_visits_per_month", sa.Integer(), nullable=False), sa.ForeignKeyConstraint(["organization_id"],["organizations.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["region_id"],["regions.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id")); pk_fk_indexes("territories")
    op.create_table("specialties", *base_columns(), org_fk(), sa.Column("name", sa.String(160), nullable=False), sa.ForeignKeyConstraint(["organization_id"],["organizations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("organization_id","name", name="uq_specialties_org_name")); pk_fk_indexes("specialties")
    op.create_table("product_categories", *base_columns(), org_fk(), sa.Column("name", sa.String(160), nullable=False), sa.ForeignKeyConstraint(["organization_id"],["organizations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id")); pk_fk_indexes("product_categories")
    op.create_table("products", *base_columns(), org_fk(), fk("category_id","product_categories"), sa.Column("name", sa.String(180), nullable=False), sa.Column("sku", sa.String(80)), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("priority_weight", sa.Float(), nullable=False), sa.ForeignKeyConstraint(["organization_id"],["organizations.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["category_id"],["product_categories.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id")); pk_fk_indexes("products")
    op.create_table("hcps", *base_columns(), org_fk(), sa.Column("territory_id", postgresql.UUID(as_uuid=True), nullable=False), fk("specialty_id","specialties"), sa.Column("first_name", sa.String(120), nullable=False), sa.Column("last_name", sa.String(120), nullable=False), sa.Column("npi", sa.String(40)), sa.Column("email", sa.String(320)), sa.Column("phone", sa.String(40)), sa.Column("engagement_score", sa.Float(), nullable=False), sa.Column("prescription_trend", sa.Float(), nullable=False), sa.Column("manager_adjustment", sa.Float(), nullable=False), sa.ForeignKeyConstraint(["organization_id"],["organizations.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["territory_id"],["territories.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["specialty_id"],["specialties.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id")); pk_fk_indexes("hcps")
    for table in ["addresses","campaigns","product_priority_rules","visits","visit_notes","call_objectives","recommendations","interactions","routes","route_stops","calendar_events","activities","attachments","notifications","settings"]:
        cols = base_columns()+[org_fk()]
        if table=="addresses": cols += [fk("hcp_id","hcps"), sa.Column("line1",sa.String(255),nullable=False), sa.Column("line2",sa.String(255)), sa.Column("city",sa.String(120),nullable=False), sa.Column("state",sa.String(80),nullable=False), sa.Column("postal_code",sa.String(20),nullable=False), sa.Column("country",sa.String(80),nullable=False), sa.Column("latitude",sa.Float()), sa.Column("longitude",sa.Float())]
        elif table=="campaigns": cols += [fk("product_id","products"), sa.Column("name",sa.String(180),nullable=False), sa.Column("starts_on",sa.Date()), sa.Column("ends_on",sa.Date()), sa.Column("weight",sa.Float(),nullable=False), sa.Column("is_active",sa.Boolean(),nullable=False)]
        elif table=="product_priority_rules": cols += [sa.Column("product_id",postgresql.UUID(as_uuid=True),nullable=False), fk("territory_id","territories"), sa.Column("weight",sa.Float(),nullable=False), sa.Column("criteria",postgresql.JSONB(),nullable=False)]
        elif table=="visits": cols += [sa.Column("hcp_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("user_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("scheduled_at",sa.DateTime(timezone=True),nullable=False), sa.Column("completed_at",sa.DateTime(timezone=True)), sa.Column("status",sa.String(40),nullable=False), sa.Column("outcome",sa.Text())]
        elif table=="visit_notes": cols += [sa.Column("visit_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("author_user_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("note_type",sa.String(40),nullable=False), sa.Column("content",sa.Text(),nullable=False)]
        elif table=="call_objectives": cols += [sa.Column("hcp_id",postgresql.UUID(as_uuid=True),nullable=False), fk("product_id","products"), sa.Column("title",sa.String(200),nullable=False), sa.Column("status",sa.String(40),nullable=False), sa.Column("due_at",sa.DateTime(timezone=True))]
        elif table=="recommendations": cols += [sa.Column("hcp_id",postgresql.UUID(as_uuid=True),nullable=False), fk("product_id","products"), sa.Column("title",sa.String(200),nullable=False), sa.Column("rationale",sa.Text(),nullable=False), sa.Column("score",sa.Float(),nullable=False), sa.Column("status",sa.String(40),nullable=False)]
        elif table=="interactions": cols += [sa.Column("hcp_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("user_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("channel",sa.String(40),nullable=False), sa.Column("occurred_at",sa.DateTime(timezone=True),nullable=False), sa.Column("summary",sa.Text(),nullable=False), sa.Column("sentiment",sa.String(40))]
        elif table=="routes": cols += [sa.Column("user_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("name",sa.String(180),nullable=False), sa.Column("route_date",sa.Date(),nullable=False), sa.Column("status",sa.String(40),nullable=False)]
        elif table=="route_stops": cols += [sa.Column("route_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("hcp_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("sequence",sa.Integer(),nullable=False), sa.Column("planned_arrival_at",sa.DateTime(timezone=True)), sa.Column("planned_departure_at",sa.DateTime(timezone=True)), sa.Column("travel_minutes",sa.Integer())]
        elif table=="calendar_events": cols += [sa.Column("user_id",postgresql.UUID(as_uuid=True),nullable=False), fk("hcp_id","hcps"), sa.Column("title",sa.String(200),nullable=False), sa.Column("starts_at",sa.DateTime(timezone=True),nullable=False), sa.Column("ends_at",sa.DateTime(timezone=True),nullable=False), sa.Column("event_type",sa.String(40),nullable=False)]
        elif table=="activities": cols += [fk("user_id","users"), sa.Column("entity_type",sa.String(80),nullable=False), sa.Column("entity_id",postgresql.UUID(as_uuid=True)), sa.Column("action",sa.String(80),nullable=False), sa.Column("description",sa.Text(),nullable=False)]
        elif table=="attachments": cols += [sa.Column("uploaded_by_user_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("entity_type",sa.String(80),nullable=False), sa.Column("entity_id",postgresql.UUID(as_uuid=True)), sa.Column("file_name",sa.String(255),nullable=False), sa.Column("content_type",sa.String(120),nullable=False), sa.Column("storage_key",sa.String(500),nullable=False), sa.Column("size_bytes",sa.Integer(),nullable=False), sa.UniqueConstraint("storage_key")]
        elif table=="notifications": cols += [sa.Column("user_id",postgresql.UUID(as_uuid=True),nullable=False), sa.Column("title",sa.String(200),nullable=False), sa.Column("body",sa.Text(),nullable=False), sa.Column("notification_type",sa.String(60),nullable=False), sa.Column("read_at",sa.DateTime(timezone=True)), sa.Column("metadata",postgresql.JSONB(),nullable=False)]
        elif table=="settings": cols += [sa.Column("scope",sa.String(80),nullable=False), sa.Column("key",sa.String(160),nullable=False), sa.Column("value",postgresql.JSONB(),nullable=False), sa.UniqueConstraint("organization_id","scope","key", name="uq_settings_org_scope_key")]
        cols += [sa.ForeignKeyConstraint(["organization_id"],["organizations.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id")]
        op.create_table(table, *cols); pk_fk_indexes(table)

    fk_specs = [
        ("addresses", "hcp_id", "hcps", "CASCADE"), ("campaigns", "product_id", "products", "SET NULL"),
        ("product_priority_rules", "product_id", "products", "CASCADE"), ("product_priority_rules", "territory_id", "territories", "CASCADE"),
        ("visits", "hcp_id", "hcps", "CASCADE"), ("visits", "user_id", "users", "RESTRICT"),
        ("visit_notes", "visit_id", "visits", "CASCADE"), ("visit_notes", "author_user_id", "users", "RESTRICT"),
        ("call_objectives", "hcp_id", "hcps", "CASCADE"), ("call_objectives", "product_id", "products", "SET NULL"),
        ("recommendations", "hcp_id", "hcps", "CASCADE"), ("recommendations", "product_id", "products", "SET NULL"),
        ("interactions", "hcp_id", "hcps", "CASCADE"), ("interactions", "user_id", "users", "RESTRICT"),
        ("routes", "user_id", "users", "RESTRICT"), ("route_stops", "route_id", "routes", "CASCADE"), ("route_stops", "hcp_id", "hcps", "CASCADE"),
        ("calendar_events", "user_id", "users", "CASCADE"), ("calendar_events", "hcp_id", "hcps", "SET NULL"),
        ("activities", "user_id", "users", "SET NULL"), ("attachments", "uploaded_by_user_id", "users", "RESTRICT"), ("notifications", "user_id", "users", "CASCADE"),
    ]
    for table, col, ref, ondelete in fk_specs:
        op.create_foreign_key(f"fk_{table}_{col}_{ref}", table, ref, [col], ["id"], ondelete=ondelete)

def downgrade():
    for table in ["settings","notifications","attachments","activities","calendar_events","route_stops","routes","interactions","recommendations","call_objectives","visit_notes","visits","product_priority_rules","campaigns","addresses","hcps","products","product_categories","specialties","territories","regions"]:
        op.drop_table(table)
