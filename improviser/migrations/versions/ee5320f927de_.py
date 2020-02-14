"""empty message

Revision ID: ee5320f927de
Revises: 5b825020b4db
Create Date: 2020-01-28 17:46:07.544327

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ee5320f927de'
down_revision = '5b825020b4db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recent_riff_exercises',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('riff_exercise_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['riff_exercise_id'], ['riff_exercises.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recent_riff_exercises_id'), 'recent_riff_exercises', ['id'], unique=False)
    op.create_index(op.f('ix_recent_riff_exercises_riff_exercise_id'), 'recent_riff_exercises', ['riff_exercise_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_recent_riff_exercises_riff_exercise_id'), table_name='recent_riff_exercises')
    op.drop_index(op.f('ix_recent_riff_exercises_id'), table_name='recent_riff_exercises')
    op.drop_table('recent_riff_exercises')
    # ### end Alembic commands ###