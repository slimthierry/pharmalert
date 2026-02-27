import enum

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class InteractionSeverity(str, enum.Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CONTRAINDICATED = "contraindicated"


class Interaction(Base, TimestampMixin):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medication_a_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medications.id"), nullable=False, index=True
    )
    medication_b_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medications.id"), nullable=False, index=True
    )
    severity: Mapped[InteractionSeverity] = mapped_column(
        Enum(InteractionSeverity), nullable=False
    )
    mechanism: Mapped[str] = mapped_column(Text, nullable=True)
    clinical_effect: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=True)

    # Relationships
    medication_a = relationship(
        "Medication", back_populates="interactions_as_a", foreign_keys=[medication_a_id]
    )
    medication_b = relationship(
        "Medication", back_populates="interactions_as_b", foreign_keys=[medication_b_id]
    )

    def __repr__(self) -> str:
        return (
            f"<Interaction(id={self.id}, "
            f"med_a={self.medication_a_id}, "
            f"med_b={self.medication_b_id}, "
            f"severity={self.severity})>"
        )
