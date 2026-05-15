import enum
from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AllergenType(str, enum.Enum):
    MEDICATION = "medication"
    FOOD = "food"
    ENVIRONMENTAL = "environmental"


class AllergySeverity(str, enum.Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    LIFE_THREATENING = "life_threatening"


class ReactionType(str, enum.Enum):
    RASH = "rash"
    ANAPHYLAXIS = "anaphylaxis"
    NAUSEA = "nausea"
    RESPIRATORY = "respiratory"
    OTHER = "other"


class PatientAllergy(Base, TimestampMixin):
    __tablename__ = "patient_allergies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Patient link (via Patient model)
    patient_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=True
    )
    # Legacy: keep patient_ipp for existing data
    patient_ipp: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, index=True
    )

    # SIH reference
    sih_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    allergen_type: Mapped[AllergenType] = mapped_column(
        Enum(AllergenType), nullable=False
    )
    allergen_name: Mapped[str] = mapped_column(String(255), nullable=False)
    atc_code: Mapped[str] = mapped_column(
        String(10), nullable=True,
        comment="ATC code if allergen is a medication"
    )
    severity: Mapped[AllergySeverity] = mapped_column(
        Enum(AllergySeverity), nullable=False, default=AllergySeverity.MODERATE
    )
    reaction_type: Mapped[ReactionType] = mapped_column(
        Enum(ReactionType), nullable=False, default=ReactionType.OTHER
    )
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reported_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # Relations
    patient: Mapped[Optional["Patient"]] = relationship("Patient", back_populates="allergies")

    def __repr__(self) -> str:
        return (
            f"<PatientAllergy(id={self.id}, patient_ipp={self.patient_ipp}, "
            f"allergen={self.allergen_name})>"
        )
