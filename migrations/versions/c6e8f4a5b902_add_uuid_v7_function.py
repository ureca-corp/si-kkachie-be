"""add uuid_generate_v7 function

Revision ID: c6e8f4a5b902
Revises: b5d7e3f4a891
Create Date: 2026-01-27 17:10:00.000000

UUID v7 provides time-sortable UUIDs which improve database performance
by reducing index fragmentation compared to random UUID v4.

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c6e8f4a5b902'
down_revision: str | Sequence[str] | None = 'b5d7e3f4a891'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create uuid_generate_v7 function for PostgreSQL."""
    # UUID v7 implementation for PostgreSQL
    # Based on RFC 9562 - time-ordered UUIDs
    op.execute("""
        CREATE OR REPLACE FUNCTION uuid_generate_v7()
        RETURNS uuid
        AS $$
        DECLARE
            unix_ts_ms bytea;
            uuid_bytes bytea;
        BEGIN
            -- Get current timestamp in milliseconds
            unix_ts_ms = substring(int8send(floor(extract(epoch from clock_timestamp()) * 1000)::bigint) from 3);

            -- Build the uuid bytes
            uuid_bytes = unix_ts_ms || gen_random_bytes(10);

            -- Set version (7) and variant (2) bits
            uuid_bytes = set_byte(uuid_bytes, 6, (b'0111' || get_byte(uuid_bytes, 6)::bit(4))::bit(8)::int);
            uuid_bytes = set_byte(uuid_bytes, 8, (b'10' || get_byte(uuid_bytes, 8)::bit(6))::bit(8)::int);

            RETURN encode(uuid_bytes, 'hex')::uuid;
        END
        $$ LANGUAGE plpgsql VOLATILE;
    """)

    # Update all tables to use uuid_generate_v7() as default
    # Note: This only affects new rows, existing data keeps their IDs
    tables = [
        'profiles', 'translations', 'mission_templates', 'mission_steps',
        'mission_progress', 'mission_step_progress', 'phrases',
        'phrase_step_mapping', 'route_history'
    ]
    for table in tables:
        op.execute(f"ALTER TABLE {table} ALTER COLUMN id SET DEFAULT uuid_generate_v7()")


def downgrade() -> None:
    """Remove uuid_generate_v7 function."""
    # Remove default from all tables
    tables = [
        'profiles', 'translations', 'mission_templates', 'mission_steps',
        'mission_progress', 'mission_step_progress', 'phrases',
        'phrase_step_mapping', 'route_history'
    ]
    for table in tables:
        op.execute(f"ALTER TABLE {table} ALTER COLUMN id DROP DEFAULT")

    op.execute("DROP FUNCTION IF EXISTS uuid_generate_v7()")
