from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import BIGINT, ForeignKey

from app.core.database import Base


class LastMessageModel(Base):
    __tablename__ = "last_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[int] = mapped_column(BIGINT, unique=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))