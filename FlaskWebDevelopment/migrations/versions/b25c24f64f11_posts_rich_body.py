"""posts rich body

Revision ID: b25c24f64f11
Revises: 9b08ce2c3e22
Create Date: 2016-11-10 12:29:54.223550

"""

# revision identifiers, used by Alembic.
revision = 'b25c24f64f11'
down_revision = '9b08ce2c3e22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('body_html', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'body_html')
    ### end Alembic commands ###
