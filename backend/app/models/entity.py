"""
Entity models for multi-establishment support.

Each entity represents a hospital/establishment that can use PharmAlert.
Users can be assigned to one or multiple entities.
"""

from datetime import date, datetime
from typing import Optional, TYPE_CHECKING, Any

from sqlalchemy import String, Text, Boolean, Date, DateTime, ForeignKey, JSON, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user_models import User


class Entity(Base, TimestampMixin):
    """
    Represents a hospital/establishment using PharmAlert.

    This enables multi-tenant support where one PharmAlert deployment
    serves multiple hospitals or facilities.
    """
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Contact
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Location
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="Togo")

    # Branding (stored as URLs or base64 in settings)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Subscription / licensing
    subscription_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    subscription_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    max_users: Mapped[int] = mapped_column(default=50, nullable=False)

    # SIH Integration (Odoo Likmed)
    sih_config: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    last_sih_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relations
    user_assignments: Mapped[list["EntityUserAssignment"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )
    services: Mapped[list["EntityService"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )
    patients: Mapped[list["Patient"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )
    medications: Mapped[list["Medication"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, name={self.name}, code={self.code})>"

    @property
    def is_subscription_valid(self) -> bool:
        """Check if subscription is still valid."""
        today = date.today()
        if self.subscription_start and self.subscription_end:
            return self.subscription_start <= today <= self.subscription_end
        return True  # No expiry set, assume valid


class EntityUserAssignment(Base, TimestampMixin):
    """
    Links a user to an entity with optional validity period.

    A user can be assigned to multiple entities.
    One assignment can be marked as "default" for the user.
    """
    __tablename__ = "entity_user_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Validity period
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Metadata
    assigned_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    assignment_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relations
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="entity_assignments"
    )
    entity: Mapped["Entity"] = relationship(
        "Entity", back_populates="user_assignments"
    )

    def __repr__(self) -> str:
        return f"<EntityUserAssignment(user_id={self.user_id}, entity_id={self.entity_id})>"

    @property
    def is_valid(self) -> bool:
        """Check if the assignment is currently valid."""
        today = date.today()
        if not self.is_active:
            return False
        if self.start_date and self.end_date:
            return self.start_date <= today <= self.end_date
        if self.start_date:
            return self.start_date <= today
        if self.end_date:
            return today <= self.end_date
        return True


class EntityService(Base, TimestampMixin):
    """
    Services/departments within an entity (hospital).

    Examples: Pharmacy, Cardiology, Emergency, ICU, etc.
    """
    __tablename__ = "entity_services"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Category
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Categories: "medical", "surgical", "emergency", "support", "administration"

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)

    # Relations
    entity: Mapped["Entity"] = relationship(
        "Entity", back_populates="services"
    )

    def __repr__(self) -> str:
        return f"<EntityService(id={self.id}, name={self.name}, entity={self.entity_id})>"