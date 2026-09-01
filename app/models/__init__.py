from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    checks: Mapped[list["CheckResult"]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
        order_by="CheckResult.checked_at.desc()",
    )


class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(10))
    status_code: Mapped[int | None]
    response_time_ms: Mapped[float | None]
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    error_message: Mapped[str | None] = mapped_column(String(2048))

    service: Mapped[Service] = relationship(back_populates="checks")
