"""Add status field to Upload model

Revision ID: [your_revision_id]
Revises: 
Create Date: 2025-11-13 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '[your_revision_id]'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # First add the column as nullable
    with op.batch_alter_table('uploads') as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(), nullable=True))
    
    # Then update all existing rows to have a default value
    op.execute("UPDATE uploads SET status = 'uploaded' WHERE status IS NULL")
    
    # Finally, alter the column to be NOT NULL
    with op.batch_alter_table('uploads') as batch_op:
        batch_op.alter_column('status', 
                            existing_type=sa.String(),
                            nullable=False,
                            server_default='uploaded')

def downgrade():
    with op.batch_alter_table('uploads') as batch_op:
        batch_op.drop_column('status')