"""initial migration

Revision ID: 523e43727721
Revises: 
Create Date: 2017-12-22 12:50:02.312623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '523e43727721'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('category')
    op.drop_table('item')
    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('user_id_seq'::regclass)"), nullable=False),
    sa.Column('username', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('picture', sa.VARCHAR(length=250), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('email', name='user_email_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('item',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=1024), autoincrement=False, nullable=True),
    sa.Column('category_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('creator_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('edited_time', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], name='item_category_id_fkey'),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], name='item_creator_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='item_pkey')
    )
    op.create_table('category',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('creator_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], name='category_creator_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='category_pkey')
    )
    # ### end Alembic commands ###
