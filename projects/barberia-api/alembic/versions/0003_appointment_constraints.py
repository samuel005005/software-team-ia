"""T-024..T-025: constraints de citas (anti-overlap + scheduled_end)."""

from typing import Sequence, Union

from alembic import op

revision: str = "0003_appointment_constraints"
down_revision: Union[str, None] = "0002_domain_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.create_check_constraint(
        "ck_appointments_scheduled_range",
        "appointments",
        "scheduled_end > scheduled_start",
    )

    op.execute(
        """
        ALTER TABLE appointments
        ADD CONSTRAINT ex_appointments_barber_no_overlap
        EXCLUDE USING gist (
            barber_user_id WITH =,
            tstzrange(scheduled_start, scheduled_end, '[)') WITH &&
        )
        WHERE (status NOT IN ('cancelada'))
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE appointments DROP CONSTRAINT IF EXISTS ex_appointments_barber_no_overlap"
    )
    op.drop_constraint("ck_appointments_scheduled_range", "appointments", type_="check")
