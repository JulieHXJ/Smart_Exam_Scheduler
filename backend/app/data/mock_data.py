from app.models.exam import Exam, ExamCategory, ExamType
from app.models.registration import Registration
from app.models.room import Room, RoomType
from app.models.student import Student


# 5 exams, 3 rooms, 10 students, and 20 registrations
exams = [
    Exam(
        id="exam_math1",
        exam_number="9870040",
        title="Mathematics 1",
        study_program="IIS",
        semester=1,
        duration_minutes=60,
        examiner_ids=["examiner_justen"],
        exam_type=ExamType.WRITTEN,
        category=ExamCategory.REGULAR,
    ),
    Exam(
        id="exam_prog1",
        exam_number="9870010",
        title="Programming 1",
        study_program="IIS",
        semester=1,
        duration_minutes=60,
        examiner_ids=["examiner_lauterbach"],
        exam_type=ExamType.DIGITAL,
        category=ExamCategory.REGULAR,
    ),
    Exam(
        id="exam_db",
        exam_number="9870200",
        title="Database Systems",
        study_program="IIS",
        semester=3,
        duration_minutes=90,
        examiner_ids=["examiner_kolonko"],
        exam_type=ExamType.WRITTEN,
        category=ExamCategory.REGULAR,
    ),
    Exam(
        id="exam_stats",
        exam_number="9870300",
        title="Statistics",
        study_program="IIS",
        semester=4,
        duration_minutes=90,
        examiner_ids=["examiner_strasser"],
        exam_type=ExamType.WRITTEN,
        category=ExamCategory.REGULAR,
    ),
    Exam(
        id="exam_security",
        exam_number="9870400",
        title="Cryptography and Security",
        study_program="IIS",
        semester=5,
        duration_minutes=90,
        examiner_ids=[
            "examiner_hollmann",
            "examiner_werthschulte",
        ],
        exam_type=ExamType.WRITTEN,
        category=ExamCategory.ELECTIVE,
    ),
]


rooms = [
    Room(
        id="room_m101",
        name="M1.01",
        capacity=45,
        room_type=RoomType.EXAM_ROOM,
    ),
    Room(
        id="room_m102",
        name="M1.02",
        capacity=45,
        room_type=RoomType.EXAM_ROOM,
    ),
    Room(
        id="room_m202",
        name="M2.02",
        capacity=20,
        room_type=RoomType.LAB,
    ),
]


students = [
    Student(id="student_001"),
    Student(id="student_002"),
    Student(id="student_003"),
    Student(id="student_004"),
    Student(id="student_005"),
    Student(id="student_006"),
    Student(id="student_007"),
    Student(id="student_008"),
    Student(id="student_009"),
    Student(id="student_010"),
]


registrations = [
    Registration(student_id="student_001", exam_id="exam_math1"),
    Registration(student_id="student_001", exam_id="exam_prog1"),

    Registration(student_id="student_002", exam_id="exam_math1"),
    Registration(student_id="student_002", exam_id="exam_prog1"),

    Registration(student_id="student_003", exam_id="exam_math1"),
    Registration(student_id="student_003", exam_id="exam_db"),

    Registration(student_id="student_004", exam_id="exam_prog1"),
    Registration(student_id="student_004", exam_id="exam_db"),

    Registration(student_id="student_005", exam_id="exam_stats"),
    Registration(student_id="student_005", exam_id="exam_security"),

    Registration(student_id="student_006", exam_id="exam_math1"),
    Registration(student_id="student_006", exam_id="exam_stats"),

    Registration(student_id="student_007", exam_id="exam_prog1"),
    Registration(student_id="student_007", exam_id="exam_security"),

    Registration(student_id="student_008", exam_id="exam_db"),
    Registration(student_id="student_009", exam_id="exam_stats"),
    Registration(student_id="student_010", exam_id="exam_security"),
]