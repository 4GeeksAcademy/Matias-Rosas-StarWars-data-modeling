"""empty message

Revision ID: 37fc4f1c3d7b
Revises: 1f3bdb2ce0c0
Create Date: 2024-11-20 23:42:05.946441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37fc4f1c3d7b'
down_revision = '1f3bdb2ce0c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('characters_favorites',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('character_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('characters_favorites')
    # ### end Alembic commands ###
