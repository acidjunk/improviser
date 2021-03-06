"""empty message

Revision ID: 99d16a0b769d
Revises: 
Create Date: 2017-12-16 00:39:31.456795

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "99d16a0b769d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "riffs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("number_of_bars", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("chord", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_riffs_chord"), "riffs", ["chord"], unique=False)
    op.create_index(op.f("ix_riffs_name"), "riffs", ["name"], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_riffs_name"), table_name="riffs")
    op.drop_index(op.f("ix_riffs_chord"), table_name="riffs")
    op.drop_table("riffs")
    # ### end Alembic commands ###
