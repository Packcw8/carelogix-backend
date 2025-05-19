"""Clean UUID client IDs

Revision ID: 486ad2225cf1
Revises: 804f34f3329f
Create Date: 2025-05-19 10:57:31.977211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '486ad2225cf1'
down_revision: Union[str, None] = '804f34f3329f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Deletes clients where the ID is a string UUID (matches hex + dashes)
    op.execute("DELETE FROM clients WHERE id ~ '^[0-9a-fA-F-]+$';")

def downgrade():
    # You can't restore deleted rows, so this downgrade is a no-op
    pass