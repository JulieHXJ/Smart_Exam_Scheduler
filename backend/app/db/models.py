from datetime import date
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.models.room import RoomType


class Base(DeclarativeBase):
    pass


class ProgramCode(str, Enum):
    IIS = "IIS"
    WI = "WI"
    IN = "IN"
    TI = "TI"
    KIR = "KIR"
    WPF = "WPF"
    ITPM = "ITPM"
    SE = "SE"


class StudyPlan(Base):
    __tablename__ = "study_plans"
    __table_args__ = (
        sa.UniqueConstraint("program_code", "spo_version", name="uq_study_plan_program_spo"),
        sa.CheckConstraint("valid_to IS NULL OR valid_to >= valid_from", name="ck_study_plan_dates"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    program_code: Mapped[ProgramCode] = mapped_column(
        sa.Enum(ProgramCode, native_enum=False, create_constraint=True, validate_strings=True, name="program_code")
    )
    spo_version: Mapped[str] = mapped_column(sa.String(64))
    valid_from: Mapped[date | None]
    valid_to: Mapped[date | None]
    active: Mapped[bool] = mapped_column(server_default=sa.true())


class ExamDefinition(Base):
    __tablename__ = "exam_definitions"
    __table_args__ = (
        sa.UniqueConstraint("study_plan_id", "exam_number", name="uq_exam_definition_plan_number"),
        sa.CheckConstraint("duration_minutes > 0", name="ck_exam_definition_duration"),
        sa.CheckConstraint("recommended_semester > 0", name="ck_exam_definition_semester"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    study_plan_id: Mapped[int] = mapped_column(sa.ForeignKey("study_plans.id"), index=True)
    exam_number: Mapped[str | None] = mapped_column(sa.String(64), index=True)
    title: Mapped[str] = mapped_column(sa.String(255))
    recommended_semester: Mapped[int | None]
    duration_minutes: Mapped[int]
    exam_type: Mapped[str] = mapped_column(
        sa.Enum("written", "digital", "oral", native_enum=False,
                create_constraint=True, validate_strings=True, name="final_exam_type")
    )
    is_mandatory: Mapped[bool]
    study_plan: Mapped[StudyPlan] = relationship()


class Examiner(Base):
    __tablename__ = "examiners"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(255))


class ExamDefinitionExaminer(Base):
    __tablename__ = "exam_definition_examiners"

    exam_definition_id: Mapped[int] = mapped_column(
        sa.ForeignKey("exam_definitions.id", ondelete="CASCADE"), primary_key=True
    )
    examiner_id: Mapped[int] = mapped_column(
        sa.ForeignKey("examiners.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    role: Mapped[str | None] = mapped_column(sa.String(64))
    exam_definition: Mapped[ExamDefinition] = relationship()
    examiner: Mapped[Examiner] = relationship()


class MappingGroup(Base):
    __tablename__ = "mapping_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(255))


class MappingMember(Base):
    __tablename__ = "mapping_members"

    mapping_group_id: Mapped[int] = mapped_column(
        sa.ForeignKey("mapping_groups.id", ondelete="CASCADE"), primary_key=True
    )
    exam_definition_id: Mapped[int] = mapped_column(
        sa.ForeignKey("exam_definitions.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    mapping_group: Mapped[MappingGroup] = relationship()
    exam_definition: Mapped[ExamDefinition] = relationship()


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (
        sa.CheckConstraint("capacity >= 0", name="ck_room_capacity"),
        sa.CheckConstraint("overbooking_factor >= 1", name="ck_room_overbooking_factor"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(128), unique=True)
    capacity: Mapped[int | None]
    room_type: Mapped[RoomType] = mapped_column(
        sa.Enum(RoomType, values_callable=lambda enum: [item.value for item in enum],
                native_enum=False, create_constraint=True, validate_strings=True, name="room_type")
    )
    overbooking_factor: Mapped[float | None]
