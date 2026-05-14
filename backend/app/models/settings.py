"""
System configuration models.

Provides a key-value store for system-wide settings, similar to Odoo's ir.config_parameter.
Settings are organized by groups and can be secret (hidden in UI).
"""

from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, Text, Boolean, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SystemConfig(Base):
    """
    Global key-value settings store.

    Groups:
    - branding: logo, name, colors
    - integrations: MinIO, SMS, WhatsApp, FHIR
    - security: session timeout, password policy
    - notifications: email, SMS enabled
    - billing: invoice settings, deposit rules
    - medical: interaction check rules, validation workflow
    """
    __tablename__ = "system_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # The setting key (e.g., "brand.name", "sms.enabled")
    key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # The setting value (stored as JSON string for flexibility)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Organization
    group: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    # Common groups: branding, integrations, security, notifications, billing, medical, general

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Behavior flags
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_editable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Value constraints
    value_type: Mapped[str] = mapped_column(
        String(50), default="string", nullable=False
    )
    # Types: string, boolean, integer, float, json, url, email

    # Validation
    default_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    choices: Mapped[Optional[str]] = mapped_column(
        # JSON array of valid choices, e.g., '["option1", "option2"]'
        Text, nullable=True
    )

    # Scope
    is_global: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="If True, applies to all entities. If False, per-entity config."
    )
    entity_id: Mapped[Optional[int]] = mapped_column(nullable=True, index=True)

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=lambda: datetime.now(),
        nullable=False
    )
    created_by: Mapped[Optional[int]] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<SystemConfig(key={self.key}, group={self.group})>"

    def get_value(self) -> Any:
        """
        Get the parsed value based on value_type.

        Returns the appropriate Python type.
        """
        if self.value is None:
            return self._parse_value(self.default_value)

        return self._parse_value(self.value)

    def _parse_value(self, raw: Optional[str]) -> Any:
        """Parse a JSON string to the appropriate Python type."""
        import json

        if raw is None:
            return None

        if self.value_type == "boolean":
            return raw.lower() in ("true", "1", "yes", "on")

        if self.value_type == "integer":
            try:
                return int(raw)
            except (ValueError, TypeError):
                return None

        if self.value_type == "float":
            try:
                return float(raw)
            except (ValueError, TypeError):
                return None

        if self.value_type == "json":
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                return None

        return raw  # string, url, email

    def set_value(self, val: Any) -> None:
        """Set the value from a Python type."""
        import json

        if val is None:
            self.value = None
            return

        if isinstance(val, bool):
            self.value = "true" if val else "false"
        elif isinstance(val, (int, float)):
            self.value = str(val)
        elif isinstance(val, (dict, list)):
            self.value = json.dumps(val)
        else:
            self.value = str(val)


class ConfigGroup(Base):
    """
    Groups multiple SystemConfig entries under a logical category.

    Used to organize settings in the admin UI.
    """
    __tablename__ = "config_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<ConfigGroup(key={self.key}, name={self.name})>"