import enum
from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import Enum, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.entity import EntityUserAssignment


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

    # Multi-entity support
    can_access_all_entities: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    prescriptions = relationship(
        "Prescription", back_populates="prescriber", foreign_keys="Prescription.prescriber_id"
    )
    validated_prescriptions = relationship(
        "Prescription", back_populates="validator", foreign_keys="Prescription.validated_by"
    )
    administrations = relationship("Administration", back_populates="nurse")
    entity_assignments: Mapped[list["EntityUserAssignment"]] = relationship(
        "EntityUserAssignment",
        foreign_keys="EntityUserAssignment.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
