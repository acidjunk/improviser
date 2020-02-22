"""empty message

Revision ID: 7418f933e467
Revises: b618481ac94e
Create Date: 2019-04-12 23:02:23.517470

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7418f933e467"
down_revision = "b618481ac94e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "riff_exercise_instruments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("riff_exercise_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("instrument_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["instrument_id"], ["instruments.id"],),
        sa.ForeignKeyConstraint(["riff_exercise_id"], ["riff_exercises.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_riff_exercise_instruments_id"), "riff_exercise_instruments", ["id"], unique=False)
    op.create_index(
        op.f("ix_riff_exercise_instruments_instrument_id"), "riff_exercise_instruments", ["instrument_id"], unique=False
    )
    op.create_index(
        op.f("ix_riff_exercise_instruments_riff_exercise_id"),
        "riff_exercise_instruments",
        ["riff_exercise_id"],
        unique=False,
    )
    op.add_column("riff_exercises", sa.Column("stars", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("riff_exercises", "stars")
    op.drop_index(op.f("ix_riff_exercise_instruments_riff_exercise_id"), table_name="riff_exercise_instruments")
    op.drop_index(op.f("ix_riff_exercise_instruments_instrument_id"), table_name="riff_exercise_instruments")
    op.drop_index(op.f("ix_riff_exercise_instruments_id"), table_name="riff_exercise_instruments")
    op.drop_table("riff_exercise_instruments")
    # ### end Alembic commands ###
