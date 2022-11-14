"""answer_timestamp to questions_users

Revision ID: d38a8a34d148
Revises: 4b446d0b0289
Create Date: 2022-11-10 19:09:55.141188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd38a8a34d148'
down_revision = '4b446d0b0289'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('questions_users', sa.Column('answer_timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('questions_users', 'answer_timestamp')
    # ### end Alembic commands ###