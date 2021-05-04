from pydantic import BaseModel
from typing import List

class HomeworkData(BaseModel):
    id: int
    status: str
    homework_name: str
    reviewer_comment: str
    lesson_name: str

class Homeworks(BaseModel):
    homeworks: List[HomeworkData]
    current_date: int
