import enum

from sqlalchemy import Enum, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


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
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    dci: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Denomination Commune Internationale"
    )
    atc_code: Mapped[str] = mapped_column(
        String(10), nullable=True, index=True,
        comment="Anatomical Therapeutic Chemical code"
    )
    form: Mapped[MedicationForm] = mapped_column(
        Enum(MedicationForm), nullable=False, default=MedicationForm.TABLET
    )
    dosage_unit: Mapped[str] = mapped_column(String(50), nullable=False, default="mg")
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=True)
    contraindications: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    side_effects: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
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
