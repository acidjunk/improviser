"""empty message

Revision ID: 95b23230231e
Revises: 905df1c965d6
Create Date: 2023-12-01 12:40:44.635790

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = '95b23230231e'
down_revision = '905df1c965d6'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """INSERT INTO role (id, name, description) VALUES 
            (:id, :name, :description);"""
        ),
        id='4ad72d68-357e-42c5-b58b-b77349114376',
        name='school',
        description='Can view Riffs and Exercises and Lessons. Make and edit lessons and public exercises. Can manage teachers and students.',
    )


def downgrade():
    pass
