from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"))

    users = relationship("User", back_populates="department")
    jobs = relationship("Job", back_populates="department")
