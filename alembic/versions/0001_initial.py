"""Initial schema

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision      = "0001_initial"
down_revision = None
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.create_table("users",
        sa.Column("id",              sa.Integer(),  primary_key=True),
        sa.Column("name",            sa.String(),   nullable=False),
        sa.Column("email",           sa.String(),   nullable=False,
                  unique=True),
        sa.Column("hashed_password", sa.String(),   nullable=False),
        sa.Column("role",            sa.String(),
                  server_default="customer"),
        sa.Column("is_active",       sa.Boolean(),
                  server_default="true"),
        sa.Column("created_at",      sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table("customers",
        sa.Column("id",      sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id"),
                  nullable=False, unique=True),
        sa.Column("name",    sa.String(),  nullable=False),
        sa.Column("email",   sa.String(),  nullable=False, unique=True),
    )

    op.create_table("orders",
        sa.Column("id",          sa.Integer(),  primary_key=True),
        sa.Column("customer_id", sa.Integer(),
                  sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("product",     sa.String(),   nullable=False),
        sa.Column("quantity",    sa.Integer(),
                  server_default="1"),
        sa.Column("status",      sa.String(),
                  server_default="Processing"),
        sa.Column("delivery_date", sa.DateTime(), nullable=True),
        sa.Column("created_at",    sa.DateTime(), nullable=True),
    )

    op.create_table("order_requests",
        sa.Column("id",         sa.Integer(),  primary_key=True),
        sa.Column("order_id",   sa.Integer(),
                  sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("type",       sa.String(),   nullable=False),
        sa.Column("reason",     sa.Text(),     nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("email_sent", sa.Boolean(),
                  server_default="false"),
    )

    op.create_table("chat_sessions",
        sa.Column("id",         sa.String(),    primary_key=True),
        sa.Column("user_id",    sa.Integer(),
                  sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title",      sa.String(120),
                  server_default="New Chat"),
        sa.Column("created_at", sa.DateTime(),  nullable=True),
        sa.Column("updated_at", sa.DateTime(),  nullable=True),
    )
    op.create_index("ix_chat_sessions_user_id",
                    "chat_sessions", ["user_id"])

    op.create_table("messages",
        sa.Column("id",         sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(),
                  sa.ForeignKey("chat_sessions.id",
                                ondelete="CASCADE"),
                  nullable=False),
        sa.Column("role",       sa.String(10), nullable=False),
        sa.Column("content",    sa.Text(),     nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_messages_session_id",
                    "messages", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_messages_session_id", "messages")
    op.drop_table("messages")
    op.drop_index("ix_chat_sessions_user_id", "chat_sessions")
    op.drop_table("chat_sessions")
    op.drop_table("order_requests")
    op.drop_table("orders")
    op.drop_table("customers")
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")
