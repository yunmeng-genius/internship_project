from sqlalchemy import Column, PrimaryKeyConstraint

from .database import Base


class HotWord(Base):
    __tablename__ = "hot_words"

    id = Column(str, index=True)
    hotWord = Column(str)

    __table_args__ = (
        PrimaryKeyConstraint(id, hotWord),
        {},
    )
