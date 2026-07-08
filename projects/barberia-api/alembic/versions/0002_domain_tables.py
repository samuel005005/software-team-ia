"""T-020..T-023: tablas de dominio MVP."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_domain_tables"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role_enum = postgresql.ENUM(
    "client",
    "barber",
    "admin",
    name="user_role",
    create_type=False,
)

appointment_status_enum = postgresql.ENUM(
    "pendiente",
    "confirmada",
    "en_progreso",
    "completada",
    "cancelada",
    "no_show",
    name="appointment_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    user_role_enum.create(bind, checkfirst=True)
    appointment_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "client_profiles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "barber_profiles",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.String(length=512), nullable=True),
        sa.Column("is_bookable", sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "services",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("price_dop", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "barber_services",
        sa.Column("barber_user_id", sa.UUID(), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["barber_user_id"], ["barber_profiles.user_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("barber_user_id", "service_id"),
        sa.UniqueConstraint("barber_user_id", "service_id", name="uq_barber_services_barber_service"),
    )

    op.create_table(
        "business_hours",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("open_time", sa.Time(), nullable=False),
        sa.Column("close_time", sa.Time(), nullable=False),
        sa.Column("is_closed", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint("weekday >= 1 AND weekday <= 7", name="ck_business_hours_weekday"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "barber_availability",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("barber_user_id", sa.UUID(), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.CheckConstraint("weekday >= 1 AND weekday <= 7", name="ck_barber_availability_weekday"),
        sa.ForeignKeyConstraint(["barber_user_id"], ["barber_profiles.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_barber_availability_barber_user_id"), "barber_availability", ["barber_user_id"])

    op.create_table(
        "appointments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("client_user_id", sa.UUID(), nullable=False),
        sa.Column("barber_user_id", sa.UUID(), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=False),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", appointment_status_enum, nullable=False),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["barber_user_id"], ["barber_profiles.user_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["client_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_appointments_barber_user_id"), "appointments", ["barber_user_id"])
    op.create_index(op.f("ix_appointments_client_user_id"), "appointments", ["client_user_id"])
    op.create_index(op.f("ix_appointments_service_id"), "appointments", ["service_id"])

    op.create_table(
        "appointment_status_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("appointment_id", sa.UUID(), nullable=False),
        sa.Column("from_status", appointment_status_enum, nullable=True),
        sa.Column("to_status", appointment_status_enum, nullable=False),
        sa.Column("changed_by_user_id", sa.UUID(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_appointment_status_history_appointment_id"),
        "appointment_status_history",
        ["appointment_id"],
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("actor_user_id", sa.UUID(), nullable=True),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.Text(), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_actor_user_id"), "audit_logs", ["actor_user_id"])
    op.create_index(op.f("ix_audit_logs_entity_id"), "audit_logs", ["entity_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_entity_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_user_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index(op.f("ix_appointment_status_history_appointment_id"), table_name="appointment_status_history")
    op.drop_table("appointment_status_history")
    op.drop_index(op.f("ix_appointments_service_id"), table_name="appointments")
    op.drop_index(op.f("ix_appointments_client_user_id"), table_name="appointments")
    op.drop_index(op.f("ix_appointments_barber_user_id"), table_name="appointments")
    op.drop_table("appointments")
    op.drop_index(op.f("ix_barber_availability_barber_user_id"), table_name="barber_availability")
    op.drop_table("barber_availability")
    op.drop_table("business_hours")
    op.drop_table("barber_services")
    op.drop_table("services")
    op.drop_table("barber_profiles")
    op.drop_table("client_profiles")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    appointment_status_enum.drop(op.get_bind(), checkfirst=True)
    user_role_enum.drop(op.get_bind(), checkfirst=True)
