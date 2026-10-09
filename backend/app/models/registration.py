from pydantic import BaseModel

class Registration(BaseModel):
    student_id: str
    exam_id: str