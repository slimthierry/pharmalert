import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AdministrationStatus(str, enum.Enum):
    GIVEN = "given"
    REFUSED = "refused"
    MISSED = "missed"
    DELAYED = "delayed"


class Administration(Base, TimestampMixin):
    __tablename__ = "administrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prescription_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("prescriptions.id"), nullable=False, index=True
    )
    nurse_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    administered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    dose_given: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[AdministrationStatus] = mapped_column(
        Enum(AdministrationStatus), nullable=False, default=AdministrationStatus.GIVEN
    )
    patient_ipp: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    vital_signs: Mapped[dict] = mapped_column(JSON, default=dict, nullable=True)

    # Relationships
    prescription = relationship("Prescription", back_populates="administrations")
    nurse = relationship("User", back_populates="administrations")

    def __repr__(self) -> str:
        return (
            f"<Administration(id={self.id}, prescription={self.prescription_id}, "
            f"status={self.status})>"
        )
