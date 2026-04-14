"""initial schema

Revision ID: 20260409_0001
Revises:
Create Date: 2026-04-09 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260409_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """создаёт начальную схему"""

    op.create_table(
        "collections",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_collections")),
    )

    op.create_table(
        "bookmarks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bookmarks")),
        sa.UniqueConstraint("url", name=op.f("uq_bookmarks_url")),
    )

    op.create_table(
        "collection_bookmarks",
        sa.Column("collection_id", sa.Uuid(), nullable=False),
        sa.Column("bookmark_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["bookmark_id"],
            ["bookmarks.id"],
            name=op.f("fk_collection_bookmarks_bookmark_id_bookmarks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collections.id"],
            name=op.f("fk_collection_bookmarks_collection_id_collections"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "collection_id",
            "bookmark_id",
            name=op.f("pk_collection_bookmarks"),
        ),
        sa.UniqueConstraint(
            "collection_id", "bookmark_id", name="uq_collection_bookmark_pair"
        ),
    )


def downgrade() -> None:
    """удаляет начальную схему"""

    op.drop_table("collection_bookmarks")
    op.drop_table("bookmarks")
    op.drop_table("collections")
