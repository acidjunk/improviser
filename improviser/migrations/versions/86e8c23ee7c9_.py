"""empty message

Revision ID: 86e8c23ee7c9
Revises: 1d2c4f058c53
Create Date: 2020-01-09 15:12:19.341179

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '86e8c23ee7c9'
down_revision = '1d2c4f058c53'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('backing_tracks', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.drop_column('backing_tracks', 'c_available')
    op.drop_column('backing_tracks', 'created_date')
    op.drop_column('backing_tracks', 'fis_available')
    op.drop_column('backing_tracks', 'ees_available')
    op.drop_column('backing_tracks', 'f_available')
    op.drop_column('backing_tracks', 'a_available')
    op.drop_column('backing_tracks', 'd_available')
    op.drop_column('backing_tracks', 'bes_available')
    op.drop_column('backing_tracks', 'g_available')
    op.drop_column('backing_tracks', 'b_available')
    op.drop_column('backing_tracks', 'e_available')
    op.drop_column('backing_tracks', 'cis_available')
    op.drop_column('backing_tracks', 'aes_available')
    op.alter_column('riffs', 'created_date', new_column_name='created_at')
    op.alter_column('user', 'fs_uniquifier',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('riffs', 'created_at', new_column_name='created_date')
    op.alter_column('user', 'fs_uniquifier',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.add_column('backing_tracks', sa.Column('aes_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('cis_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('e_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('b_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('g_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('bes_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('d_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('a_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('f_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('ees_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('fis_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('backing_tracks', sa.Column('created_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('backing_tracks', sa.Column('c_available', sa.BOOLEAN(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
