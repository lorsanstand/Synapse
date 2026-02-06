from typing import List, Optional

from pydantic import BaseModel


class Change(BaseModel):
    field: str
    old: Optional[str]
    new: Optional[str]


class Changes(BaseModel):
    count: int
    day: str
    day_week: str
    changes: List[Change]
