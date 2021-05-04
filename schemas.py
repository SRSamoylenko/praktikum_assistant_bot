from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class HomeworkData(BaseModel):
    id: int
    status: str
    homework_name: str
    reviewer_comment: str
    date_updated: datetime
    lesson_name: str


class Homeworks(BaseModel):
    homeworks: List[HomeworkData]
    current_date: Optional[int]
