"""empty message

Revision ID: 905df1c965d6
Revises: 757548124b94
Create Date: 2023-11-07 15:13:49.535118

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '905df1c965d6'
down_revision = '757548124b94'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('schools',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_schools_id'), 'schools', ['id'], unique=False)
    op.create_table('user_relations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('school_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('teacher_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_relations_id'), 'user_relations', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_relations_id'), table_name='user_relations')
    op.drop_table('user_relations')
    op.drop_index(op.f('ix_schools_id'), table_name='schools')
    op.drop_table('schools')
    # ### end Alembic commands ###