"""Drop phone_number_encrypted column from user table

Revision ID: 8df89a4c915a
Revises: 1a31ce608336
Create Date: 2025-09-01 16:20:01.014051

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '8df89a4c915a'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('user', 'phone_number_encrypted')



def downgrade():
    op.add_column('user', sa.Column('phone_number_encrypted', sa.String(), nullable=True))

