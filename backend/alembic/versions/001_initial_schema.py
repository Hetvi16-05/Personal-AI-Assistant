"""Initial schema — all tables

Revision ID: 001
Revises:
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(200), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False, server_default=''),
        sa.Column('skills', sa.Text(), server_default=''),
        sa.Column('interests', sa.Text(), server_default=''),
        sa.Column('preferences', sa.Text(), server_default=''),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # goals
    op.create_table(
        'goals',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), server_default=''),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # projects
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('goal_id', sa.Integer(), sa.ForeignKey('goals.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), server_default=''),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # tasks
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('goal_id', sa.Integer(), sa.ForeignKey('goals.id', ondelete='SET NULL'), nullable=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), server_default=''),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('impact_score', sa.Float(), server_default='5.0'),
        sa.Column('effort_score', sa.Float(), server_default='5.0'),
        sa.Column('urgency_score', sa.Float(), server_default='5.0'),
        sa.Column('alignment_score', sa.Float(), server_default='5.0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    # user_memory
    op.create_table(
        'user_memory',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', sa.String(300), server_default=''),
        sa.Column('source', sa.String(100), server_default='chat'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # roadmaps
    op.create_table(
        'roadmaps',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('goal_id', sa.Integer(), sa.ForeignKey('goals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('summary', sa.Text(), server_default=''),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # milestones
    op.create_table(
        'milestones',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('roadmap_id', sa.Integer(), sa.ForeignKey('roadmaps.id', ondelete='CASCADE'), nullable=False),
        sa.Column('period', sa.String(100), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), server_default=''),
        sa.Column('order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # weekly_reports
    op.create_table(
        'weekly_reports',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('week_start', sa.DateTime(), nullable=False),
        sa.Column('week_end', sa.DateTime(), nullable=False),
        sa.Column('tasks_completed', sa.Integer(), server_default='0'),
        sa.Column('completion_percentage', sa.Float(), server_default='0.0'),
        sa.Column('most_active_goal', sa.String(300), server_default=''),
        sa.Column('ai_summary', sa.Text(), server_default=''),
        sa.Column('recommendations', sa.Text(), server_default=''),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # chat_sessions
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(300), server_default='New Conversation'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # chat_messages
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # memory_embeddings (pgvector)
    op.create_table(
        'memory_embeddings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('memory_text', sa.Text(), nullable=False),
        sa.Column('tags', sa.String(300), server_default=''),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    # Add vector column separately after table creation
    op.execute("ALTER TABLE memory_embeddings ADD COLUMN IF NOT EXISTS embedding vector(768)")

    # ai_insights
    op.create_table(
        'ai_insights',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('insight_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in ['ai_insights', 'memory_embeddings', 'chat_messages', 'chat_sessions',
                  'weekly_reports', 'milestones', 'roadmaps', 'user_memory',
                  'tasks', 'projects', 'goals', 'users']:
        op.drop_table(table)
