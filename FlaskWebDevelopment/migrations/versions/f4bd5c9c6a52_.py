"""empty message

Revision ID: f4bd5c9c6a52
Revises: None
Create Date: 2016-11-06 17:41:30.988856

"""

# revision identifiers, used by Alembic.
revision = 'f4bd5c9c6a52'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('roles', 'name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.create_unique_constraint(None, 'roles', ['name'])
    op.add_column('users', sa.Column('email', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.drop_column('users', 'password')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.VARCHAR(length=130), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'email')
    op.drop_constraint(None, 'roles', type_='unique')
    op.alter_column('roles', 'name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    ### end Alembic commands ###