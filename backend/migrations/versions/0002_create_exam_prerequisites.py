"""Create BZV requirements linked to final-exam definitions."""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "exam_prerequisites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exam_definition_id", sa.Integer(), nullable=False),
        sa.Column("prerequisite_number", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(
            ["exam_definition_id"], ["exam_definitions.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint(
            "exam_definition_id", "prerequisite_number",
            name="uq_exam_prerequisite_exam_number",
        ),
    )
    op.create_index(
        "ix_exam_prerequisites_exam_definition_id",
        "exam_prerequisites", ["exam_definition_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_exam_prerequisites_exam_definition_id", table_name="exam_prerequisites")
    op.drop_table("exam_prerequisites")
