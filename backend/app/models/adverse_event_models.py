import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AdverseEventType(str, enum.Enum):
    SIDE_EFFECT = "side_effect"
    ALLERGY = "allergy"
    OVERDOSE = "overdose"
    OTHER = "other"


class AdverseEventSeverity(str, enum.Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SERIOUS = "serious"
    LIFE_THREATENING = "life_threatening"


class AdverseEventStatus(str, enum.Enum):
    REPORTED = "reported"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"


class AdverseEvent(Base, TimestampMixin):
    __tablename__ = "adverse_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_ipp: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )
    medication_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medications.id"), nullable=True
    )
    prescription_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("prescriptions.id"), nullable=True
    )
    event_type: Mapped[AdverseEventType] = mapped_column(
        Enum(AdverseEventType), nullable=False
    )
    severity: Mapped[AdverseEventSeverity] = mapped_column(
        Enum(AdverseEventSeverity), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(Text, nullable=True)
    reported_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[AdverseEventStatus] = mapped_column(
        Enum(AdverseEventStatus), nullable=False, default=AdverseEventStatus.REPORTED
    )

    # Relationships
    medication = relationship("Medication", back_populates="adverse_events")
    prescription = relationship("Prescription", back_populates="adverse_events")

    def __repr__(self) -> str:
        return (
            f"<AdverseEvent(id={self.id}, patient_ipp={self.patient_ipp}, "
            f"severity={self.severity})>"
        )
