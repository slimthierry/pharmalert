import enum

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEDECIN = "medecin"
    PHARMACIEN = "pharmacien"
    INFIRMIER = "infirmier"
    PREPARATEUR = "preparateur"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.INFIRMIER
    )
    service: Mapped[str] = mapped_column(String(255), nullable=True)
    rpps_number: Mapped[str] = mapped_column(String(11), nullable=True, unique=True)

    # Relationships
    prescriptions = relationship(
        "Prescription", back_populates="prescriber", foreign_keys="Prescription.prescriber_id"
    )
    validated_prescriptions = relationship(
        "Prescription", back_populates="validator", foreign_keys="Prescription.validated_by"
    )
    administrations = relationship("Administration", back_populates="nurse")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
