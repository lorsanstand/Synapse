from typing import Any

from app.models.last_message import LastMessageModel
from app.core.dao import BaseDAO

class LastMessageDAO(BaseDAO[LastMessageModel, Any, Any]):
    model = LastMessageModel