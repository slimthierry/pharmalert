import enum
from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.entity import Entity


class MedicationForm(str, enum.Enum):
    TABLET = "tablet"
    CAPSULE = "capsule"
    INJECTION = "injection"
    SYRUP = "syrup"
    CREAM = "cream"
    PATCH = "patch"


class Medication(Base, TimestampMixin):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    dci: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Denomination Commune Internationale"
    )
    atc_code: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, index=True,
        comment="Anatomical Therapeutic Chemical code"
    )
    atc_code_original: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
        comment="Original AMM or CIP code from SIH"
    )
    active_principle: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
        comment="DCI / Principe actif"
    )
    form: Mapped[Optional[MedicationForm]] = mapped_column(
        Enum(MedicationForm), nullable=True
    )
    dosage_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=True)
    contraindications: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    side_effects: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Stock (synced from SIH)
    stock_quantity: Mapped[float] = mapped_column(
        Integer, nullable=False, default=0
    )
    is_controlled: Mapped[bool] = mapped_column(Boolean, default=False)

    # SIH reference
    sih_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Relationships
    entity: Mapped["Entity"] = relationship("Entity", back_populates="medications")
    interactions_as_a = relationship(
        "Interaction", back_populates="medication_a", foreign_keys="Interaction.medication_a_id"
    )
    interactions_as_b = relationship(
        "Interaction", back_populates="medication_b", foreign_keys="Interaction.medication_b_id"
    )
    prescriptions = relationship("Prescription", back_populates="medication")
    adverse_events = relationship("AdverseEvent", back_populates="medication")

    def __repr__(self) -> str:
        return f"<Medication(id={self.id}, name={self.name}, atc_code={self.atc_code})>"
