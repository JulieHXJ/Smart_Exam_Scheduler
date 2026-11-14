"""create reference data tables"""

from alembic import op
import sqlalchemy as sa


revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'examiners',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'mapping_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('room_type', sa.Enum('exam_room', 'lab', 'external', 'special', name='room_type', native_enum=False, create_constraint=True), nullable=False),
        sa.Column('overbooking_factor', sa.Double(), nullable=True),
        sa.CheckConstraint('capacity >= 0', name='ck_room_capacity'),
        sa.CheckConstraint('overbooking_factor >= 1', name='ck_room_overbooking_factor'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'study_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('program_code', sa.Enum('IIS', 'WI', 'IN', 'TI', 'KIR', 'WPF', 'ITPM', 'SE', name='program_code', native_enum=False, create_constraint=True), nullable=False),
        sa.Column('spo_version', sa.String(length=64), nullable=False),
        sa.Column('valid_from', sa.Date(), nullable=True),
        sa.Column('valid_to', sa.Date(), nullable=True),
        sa.Column('active', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.CheckConstraint('valid_to IS NULL OR valid_to >= valid_from', name='ck_study_plan_dates'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('program_code', 'spo_version', name='uq_study_plan_program_spo')
    )
    op.create_table(
        'exam_definitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('study_plan_id', sa.Integer(), nullable=False),
        sa.Column('exam_number', sa.String(length=64), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('recommended_semester', sa.Integer(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('exam_type', sa.Enum('written', 'digital', 'oral', name='final_exam_type', native_enum=False, create_constraint=True), nullable=False),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False),
        sa.CheckConstraint('duration_minutes > 0', name='ck_exam_definition_duration'),
        sa.CheckConstraint('recommended_semester > 0', name='ck_exam_definition_semester'),
        sa.ForeignKeyConstraint(['study_plan_id'], ['study_plans.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('study_plan_id', 'exam_number', name='uq_exam_definition_plan_number')
    )
    op.create_index(op.f('ix_exam_definitions_exam_number'), 'exam_definitions', ['exam_number'], unique=False)
    op.create_index(op.f('ix_exam_definitions_study_plan_id'), 'exam_definitions', ['study_plan_id'], unique=False)
    op.create_table(
        'exam_definition_examiners',
        sa.Column('exam_definition_id', sa.Integer(), nullable=False),
        sa.Column('examiner_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['exam_definition_id'], ['exam_definitions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['examiner_id'], ['examiners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('exam_definition_id', 'examiner_id')
    )
    op.create_index(op.f('ix_exam_definition_examiners_examiner_id'), 'exam_definition_examiners', ['examiner_id'], unique=False)
    op.create_table(
        'mapping_members',
        sa.Column('mapping_group_id', sa.Integer(), nullable=False),
        sa.Column('exam_definition_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['exam_definition_id'], ['exam_definitions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mapping_group_id'], ['mapping_groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('mapping_group_id', 'exam_definition_id')
    )
    op.create_index(op.f('ix_mapping_members_exam_definition_id'), 'mapping_members', ['exam_definition_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_mapping_members_exam_definition_id'), table_name='mapping_members')
    op.drop_table('mapping_members')
    op.drop_index(op.f('ix_exam_definition_examiners_examiner_id'), table_name='exam_definition_examiners')
    op.drop_table('exam_definition_examiners')
    op.drop_index(op.f('ix_exam_definitions_study_plan_id'), table_name='exam_definitions')
    op.drop_index(op.f('ix_exam_definitions_exam_number'), table_name='exam_definitions')
    op.drop_table('exam_definitions')
    op.drop_table('study_plans')
    op.drop_table('rooms')
    op.drop_table('mapping_groups')
    op.drop_table('examiners')
