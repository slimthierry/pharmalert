import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, EntityFilterMixin


class Patient(Base, TimestampMixin, EntityFilterMixin):
    """
    Patient model — stores patient data synced from SIH or entered manually.
    The IPP is the primary identifier.
    """
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # IPP (Identifiant Permanent Patient)
    ipp: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True, index=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(1), nullable=False, default="M")

    # Contact
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Medical info
    is_hospitalized: Mapped[bool] = mapped_column(Boolean, default=False)
    has_insurance: Mapped[bool] = mapped_column(Boolean, default=False)
    insurance_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # SIH reference (ID from external SIH system like Odoo)
    sih_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Relations
    entity: Mapped["Entity"] = relationship("Entity", back_populates="patients")
    allergies: Mapped[list["PatientAllergy"]] = relationship(
        "PatientAllergy", back_populates="patient", cascade="all, delete-orphan"
    )
    prescriptions: Mapped[list["Prescription"]] = relationship(
        "Prescription", back_populates="patient", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, ipp={self.ipp}, name={self.first_name} {self.last_name})>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
