"""add PostGIS geography columns

Revision ID: d7f9g5h6c013
Revises: c6e8f4a5b902
Create Date: 2026-01-27 17:20:00.000000

Convert separate lat/lng columns to PostGIS GEOGRAPHY(Point, 4326) type
for proper spatial indexing and geographic queries.

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision: str = 'd7f9g5h6c013'
down_revision: str | Sequence[str] | None = 'c6e8f4a5b902'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add PostGIS geography columns to route_history."""
    # Enable PostGIS extension if not exists
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Add new geography columns
    op.add_column('route_history', sa.Column(
        'start_point',
        Geography(geometry_type='POINT', srid=4326),
        nullable=True
    ))
    op.add_column('route_history', sa.Column(
        'end_point',
        Geography(geometry_type='POINT', srid=4326),
        nullable=True
    ))

    # Migrate existing data
    op.execute("""
        UPDATE route_history
        SET start_point = ST_SetSRID(ST_MakePoint(start_lng, start_lat), 4326)::geography,
            end_point = ST_SetSRID(ST_MakePoint(end_lng, end_lat), 4326)::geography
    """)

    # Make columns NOT NULL after migration
    op.alter_column('route_history', 'start_point', nullable=False)
    op.alter_column('route_history', 'end_point', nullable=False)

    # Drop old columns
    op.drop_column('route_history', 'start_lat')
    op.drop_column('route_history', 'start_lng')
    op.drop_column('route_history', 'end_lat')
    op.drop_column('route_history', 'end_lng')

    # Add spatial index
    op.create_index('ix_route_history_start_point', 'route_history', ['start_point'], postgresql_using='gist')
    op.create_index('ix_route_history_end_point', 'route_history', ['end_point'], postgresql_using='gist')


def downgrade() -> None:
    """Revert to separate lat/lng columns."""
    # Add back lat/lng columns
    op.add_column('route_history', sa.Column('start_lat', sa.Float(), nullable=True))
    op.add_column('route_history', sa.Column('start_lng', sa.Float(), nullable=True))
    op.add_column('route_history', sa.Column('end_lat', sa.Float(), nullable=True))
    op.add_column('route_history', sa.Column('end_lng', sa.Float(), nullable=True))

    # Migrate data back
    op.execute("""
        UPDATE route_history
        SET start_lat = ST_Y(start_point::geometry),
            start_lng = ST_X(start_point::geometry),
            end_lat = ST_Y(end_point::geometry),
            end_lng = ST_X(end_point::geometry)
    """)

    # Make columns NOT NULL
    op.alter_column('route_history', 'start_lat', nullable=False)
    op.alter_column('route_history', 'start_lng', nullable=False)
    op.alter_column('route_history', 'end_lat', nullable=False)
    op.alter_column('route_history', 'end_lng', nullable=False)

    # Drop indexes and geography columns
    op.drop_index('ix_route_history_start_point', table_name='route_history')
    op.drop_index('ix_route_history_end_point', table_name='route_history')
    op.drop_column('route_history', 'start_point')
    op.drop_column('route_history', 'end_point')
