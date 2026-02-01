from typing import Optional, List, Dict

from pydantic import BaseModel


class Pair(BaseModel):
    time: str
    type: str
    lesson_name: str
    teacher: str
    audience: str
    subgroup: Optional[int]


class Day(BaseModel):
    day_week: str
    pairs: Dict[str, List[Pair]]