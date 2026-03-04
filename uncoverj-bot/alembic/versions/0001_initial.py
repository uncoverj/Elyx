"""initial

Revision ID: 0001
Revises: 
Create Date: 2024-03-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- 1. users ---
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=True),
        sa.Column('is_premium', sa.Boolean(), server_default=sa.text('FALSE'), nullable=True),
        sa.Column('premium_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trust_score', sa.Float(), server_default='100.0', nullable=True),
        sa.Column('is_banned', sa.Boolean(), server_default=sa.text('FALSE'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.UniqueConstraint('telegram_id')
    )

    # --- 2. profiles ---
    op.create_table(
        'profiles',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('nickname', sa.String(length=64), nullable=False),
        sa.Column('age', sa.SmallInteger(), nullable=True),
        sa.CheckConstraint('age >= 14 AND age <= 60', name='check_age_range'),
        sa.Column('gender', sa.String(length=16), nullable=True),
        sa.Column('game_primary', sa.String(length=32), nullable=False),
        sa.Column('playstyle_tags', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=True),
        sa.Column('behavior_tags', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=True),
        sa.Column('bio_text', sa.Text(), nullable=True),
        sa.Column('photo_file_id', sa.String(length=256), nullable=True),
        sa.Column('is_visible', sa.Boolean(), server_default=sa.text('TRUE'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True)
    )

    # --- 3. accounts_link ---
    op.create_table(
        'accounts_link',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('game', sa.String(length=32), nullable=False),
        sa.Column('game_id', sa.String(length=128), nullable=False),
        sa.Column('verified', sa.Boolean(), server_default=sa.text('FALSE'), nullable=True),
        sa.UniqueConstraint('user_id', 'game', name='uq_accounts_link_user_game')
    )

    # --- 4. stats_snapshot ---
    op.create_table(
        'stats_snapshot',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('game', sa.String(length=32), nullable=False),
        sa.Column('rank_text', sa.String(length=32), nullable=True),
        sa.Column('rank_tier_id', sa.SmallInteger(), nullable=True),
        sa.Column('rank_points', sa.SmallInteger(), nullable=True),
        sa.Column('unified_score', sa.Integer(), nullable=True),
        sa.Column('kd_ratio', sa.Float(), nullable=True),
        sa.Column('winrate', sa.Float(), nullable=True),
        sa.Column('matches_played', sa.Integer(), server_default='0', nullable=True),
        sa.Column('source_status', sa.String(length=16), server_default='ok', nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.UniqueConstraint('user_id', 'game', name='uq_stats_snapshot_user_game')
    )
    op.create_index('idx_stats_game_score', 'stats_snapshot', ['game', sa.text('unified_score DESC')])

    # --- 5. swipes ---
    op.create_table(
        'swipes',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('from_user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('to_user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('game', sa.String(length=32), nullable=True),
        sa.Column('action', sa.String(length=16), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True)
    )
    op.create_index('idx_swipes_from', 'swipes', ['from_user_id', 'game'])

    # --- 6. matches ---
    op.create_table(
        'matches',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('user1_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('user2_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('game', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('status', sa.String(length=16), server_default='active', nullable=True)
    )

    # --- 7. trust_votes ---
    op.create_table(
        'trust_votes',
        sa.Column('id', sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column('voter_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('target_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('vote', sa.SmallInteger(), nullable=True),
        sa.Column('weight', sa.Float(), server_default='1.0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.UniqueConstraint('voter_id', 'target_id', name='uq_trust_votes_voter_target')
    )

    # --- 8. leaderboard_cache ---
    op.create_table(
        'leaderboard_cache',
        sa.Column('game', sa.String(length=32), primary_key=True),
        sa.Column('season', sa.String(length=16), server_default='current', nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('json_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('leaderboard_cache')
    op.drop_table('trust_votes')
    op.drop_table('matches')
    op.drop_table('swipes')
    op.drop_table('stats_snapshot')
    op.drop_table('accounts_link')
    op.drop_table('profiles')
    op.drop_table('users')
