"""Recreate migration

Revision ID: fc1f6babb1b8
Revises: 
Create Date: 2024-11-21 15:30:33.586576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc1f6babb1b8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('food_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('food_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('volume', sa.Float(), nullable=True),
    sa.Column('food_type_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('date_uploaded', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['food_type_id'], ['food_type.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('nutritional_information',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('food_item_id', sa.Integer(), nullable=False),
    sa.Column('calories', sa.Float(), nullable=True),
    sa.Column('carbs', sa.Float(), nullable=True),
    sa.Column('fat', sa.Float(), nullable=True),
    sa.Column('protein', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['food_item_id'], ['food_item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('nutritional_information')
    op.drop_table('food_item')
    op.drop_table('users')
    op.drop_table('food_type')
    # ### end Alembic commands ###
