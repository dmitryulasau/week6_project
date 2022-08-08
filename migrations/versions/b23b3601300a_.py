"""empty message

Revision ID: b23b3601300a
Revises: ff89ceac9b4a
Create Date: 2022-08-08 07:38:40.229034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b23b3601300a'
down_revision = 'ff89ceac9b4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_pokemon_name'), 'pokemon', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_pokemon_name'), table_name='pokemon')
    # ### end Alembic commands ###