import enum
from datetime import date, datetime

from sqlalchemy import Boolean, Date, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class PrescriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class ValidationStatus(str, enum.Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"


class AdministrationRoute(str, enum.Enum):
    ORAL = "oral"
    IV = "iv"
    IM = "im"
    SC = "sc"
    TOPICAL = "topical"
    INHALED = "inhaled"


class Prescription(Base, TimestampMixin):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_ipp: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True,
        comment="Identifiant Permanent du Patient"
    )
    patient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    prescriber_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    medication_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medications.id"), nullable=False
    )
    dosage_value: Mapped[float] = mapped_column(Float, nullable=False)
    dosage_unit: Mapped[str] = mapped_column(String(50), nullable=False, default="mg")
    frequency: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="e.g. 3x/day"
    )
    route: Mapped[AdministrationRoute] = mapped_column(
        Enum(AdministrationRoute), nullable=False, default=AdministrationRoute.ORAL
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[PrescriptionStatus] = mapped_column(
        Enum(PrescriptionStatus), nullable=False, default=PrescriptionStatus.ACTIVE
    )
    validation_status: Mapped[ValidationStatus] = mapped_column(
        Enum(ValidationStatus), nullable=False, default=ValidationStatus.PENDING
    )
    validated_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    validation_notes: Mapped[str] = mapped_column(Text, nullable=True)
    interactions_checked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    override_justification: Mapped[str] = mapped_column(
        Text, nullable=True,
        comment="Justification when doctor overrides a contraindicated interaction"
    )

    # Relationships
    prescriber = relationship(
        "User", back_populates="prescriptions", foreign_keys=[prescriber_id]
    )
    validator = relationship(
        "User", back_populates="validated_prescriptions", foreign_keys=[validated_by]
    )
    medication = relationship("Medication", back_populates="prescriptions")
    administrations = relationship("Administration", back_populates="prescription")
    adverse_events = relationship("AdverseEvent", back_populates="prescription")

    def __repr__(self) -> str:
        return (
            f"<Prescription(id={self.id}, patient_ipp={self.patient_ipp}, "
            f"status={self.status})>"
        )
