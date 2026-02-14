from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LinkModel(Base):
    __tablename__ = "link"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(index=True)

