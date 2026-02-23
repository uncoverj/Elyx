"""init schema

Revision ID: 20260223_0001
Revises:
Create Date: 2026-02-23 20:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260223_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tg_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_active_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_premium", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_banned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("tg_id"),
    )
    op.create_index("ix_users_tg_id", "users", ["tg_id"], unique=False)

    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "profiles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("nickname", sa.String(length=64), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("age", sa.SmallInteger(), nullable=False),
        sa.Column("game_id", sa.Integer(), sa.ForeignKey("games.id"), nullable=False),
        sa.Column("bio", sa.Text(), nullable=False),
        sa.Column("media_type", sa.String(length=16), nullable=False),
        sa.Column("media_file_id", sa.String(length=255), nullable=False),
        sa.Column("roles", sa.JSON(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_profiles_game_id", "profiles", ["game_id"], unique=False)

    op.create_table(
        "stats",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("kd", sa.Float(), nullable=True),
        sa.Column("winrate", sa.Float(), nullable=True),
        sa.Column("rank_name", sa.String(length=64), nullable=True),
        sa.Column("rank_points", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_stats_rank_name", "stats", ["rank_name"], unique=False)

    op.create_table(
        "likes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("from_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("from_user_id", "to_user_id", name="uq_likes_pair"),
    )
    op.create_index("ix_likes_from_user_id", "likes", ["from_user_id"], unique=False)
    op.create_index("ix_likes_to_user_id", "likes", ["to_user_id"], unique=False)

    op.create_table(
        "skips",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("from_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("from_user_id", "to_user_id", name="uq_skips_pair"),
    )
    op.create_index("ix_skips_from_user_id", "skips", ["from_user_id"], unique=False)
    op.create_index("ix_skips_to_user_id", "skips", ["to_user_id"], unique=False)

    op.create_table(
        "letters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("from_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_letters_from_user_id", "letters", ["from_user_id"], unique=False)
    op.create_index("ix_letters_to_user_id", "letters", ["to_user_id"], unique=False)

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_a", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_b", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_a", "user_b", name="uq_matches_pair"),
    )
    op.create_index("ix_matches_user_a", "matches", ["user_a"], unique=False)
    op.create_index("ix_matches_user_b", "matches", ["user_b"], unique=False)

    op.create_table(
        "trust_votes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("from_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("from_user_id", "to_user_id", name="uq_trust_votes_pair"),
        sa.CheckConstraint("value IN (-1, 1)", name="ck_trust_vote_value"),
    )
    op.create_index("ix_trust_votes_from_user_id", "trust_votes", ["from_user_id"], unique=False)
    op.create_index("ix_trust_votes_to_user_id", "trust_votes", ["to_user_id"], unique=False)

    op.create_table(
        "external_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=16), nullable=False),
        sa.Column("account_ref", sa.String(length=128), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "provider", name="uq_external_account_provider"),
    )
    op.create_index("ix_external_accounts_user_id", "external_accounts", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("external_accounts")
    op.drop_table("trust_votes")
    op.drop_table("matches")
    op.drop_table("letters")
    op.drop_table("skips")
    op.drop_table("likes")
    op.drop_table("stats")
    op.drop_table("profiles")
    op.drop_table("games")
    op.drop_table("users")
