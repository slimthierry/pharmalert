"""
Service layer for System Configuration management.

Provides CRUD operations and convenient access to system settings.
Supports both global and per-entity configuration.
"""

import json
from typing import Optional, Any

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import SystemConfig, ConfigGroup


class ConfigService:
    """Business logic for SystemConfig operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================
    # Config Group CRUD
    # ========================

    async def create_group(
        self,
        key: str,
        name: str,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        display_order: int = 0
    ) -> ConfigGroup:
        """Create a new config group."""
        group = ConfigGroup(
            key=key,
            name=name,
            description=description,
            icon=icon,
            display_order=display_order
        )
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def get_group(self, key: str) -> Optional[ConfigGroup]:
        """Get a config group by key."""
        result = await self.db.execute(
            select(ConfigGroup).where(ConfigGroup.key == key)
        )
        return result.scalar_one_or_none()

    async def list_groups(self, active_only: bool = True) -> list[ConfigGroup]:
        """List all config groups."""
        query = select(ConfigGroup)
        if active_only:
            query = query.where(ConfigGroup.is_active == True)
        query = query.order_by(ConfigGroup.display_order)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ========================
    # SystemConfig CRUD
    # ========================

    async def create_config(
        self,
        key: str,
        group: str,
        value: Optional[str] = None,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        is_secret: bool = False,
        is_required: bool = False,
        value_type: str = "string",
        default_value: Optional[str] = None,
        choices: Optional[str] = None,
        is_global: bool = True,
        entity_id: Optional[int] = None
    ) -> SystemConfig:
        """Create a new system config entry."""
        config = SystemConfig(
            key=key,
            group=group,
            value=value,
            description=description,
            display_name=display_name or key,
            is_secret=is_secret,
            is_required=is_required,
            value_type=value_type,
            default_value=default_value,
            choices=choices,
            is_global=is_global,
            entity_id=entity_id
        )
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def get_config(self, config_id: int) -> Optional[SystemConfig]:
        """Get a config by ID."""
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.id == config_id)
        )
        return result.scalar_one_or_none()

    async def get_config_by_key(
        self,
        key: str,
        entity_id: Optional[int] = None
    ) -> Optional[SystemConfig]:
        """
        Get a config by key.

        If entity_id is provided, first looks for per-entity config,
        then falls back to global config.
        """
        # Try entity-specific first
        if entity_id:
            result = await self.db.execute(
                select(SystemConfig).where(
                    and_(
                        SystemConfig.key == key,
                        SystemConfig.entity_id == entity_id,
                        SystemConfig.is_global == False
                    )
                )
            )
            config = result.scalar_one_or_none()
            if config:
                return config

        # Fall back to global
        result = await self.db.execute(
            select(SystemConfig).where(
                and_(
                    SystemConfig.key == key,
                    SystemConfig.is_global == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_configs(
        self,
        group: Optional[str] = None,
        entity_id: Optional[int] = None,
        include_entity_specific: bool = True,
        include_global: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[SystemConfig], int]:
        """List configs with optional filtering."""
        query = select(SystemConfig)

        conditions = []
        if group:
            conditions.append(SystemConfig.group == group)
        if not include_entity_specific:
            conditions.append(SystemConfig.is_global == True)
        if not include_global and entity_id:
            conditions.append(SystemConfig.entity_id == entity_id)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(SystemConfig.group, SystemConfig.display_name)
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        configs = result.scalars().all()

        # Count total
        count_query = select(SystemConfig)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total = await self.db.scalar(count_query.with_only_columns(SystemConfig.id).func.count())

        return list(configs), total or 0

    async def update_config(
        self,
        config_id: int,
        value: Optional[str] = None,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        is_secret: Optional[bool] = None,
        is_required: Optional[bool] = None,
        default_value: Optional[str] = None,
        choices: Optional[str] = None
    ) -> Optional[SystemConfig]:
        """Update a config entry."""
        config = await self.get_config(config_id)
        if not config:
            return None

        if not config.is_editable:
            raise ValueError(f"Config '{config.key}' is not editable")

        if value is not None:
            config.value = value
        if description is not None:
            config.description = description
        if display_name is not None:
            config.display_name = display_name
        if is_secret is not None:
            config.is_secret = is_secret
        if is_required is not None:
            config.is_required = is_required
        if default_value is not None:
            config.default_value = default_value
        if choices is not None:
            config.choices = choices

        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def update_by_key(
        self,
        key: str,
        value: Any,
        entity_id: Optional[int] = None
    ) -> Optional[SystemConfig]:
        """
        Update a config value by key.

        Finds the config (entity-specific or global) and sets the value.
        Automatically handles type conversion based on value_type.
        """
        config = await self.get_config_by_key(key, entity_id)
        if not config:
            return None

        if not config.is_editable:
            raise ValueError(f"Config '{key}' is not editable")

        # Convert value to string based on type
        if config.value_type == "boolean":
            config.value = "true" if value else "false"
        elif config.value_type in ("integer", "float"):
            config.value = str(value)
        elif config.value_type == "json":
            config.value = json.dumps(value) if isinstance(value, (dict, list)) else value
        else:
            config.value = str(value)

        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def bulk_update(
        self,
        updates: list[dict],
        entity_id: Optional[int] = None
    ) -> list[SystemConfig]:
        """
        Update multiple configs at once.

        Each update should be: {key: str, value: Any}
        """
        updated = []
        for item in updates:
            key = item.get("key")
            value = item.get("value")
            if key:
                config = await self.update_by_key(key, value, entity_id)
                if config:
                    updated.append(config)
        return updated

    async def delete_config(self, config_id: int) -> bool:
        """Delete a config entry."""
        config = await self.get_config(config_id)
        if not config:
            return False

        await self.db.delete(config)
        await self.db.commit()
        return True

    # ========================
    # Convenience Methods
    # ========================

    async def get_value(
        self,
        key: str,
        default: Any = None,
        entity_id: Optional[int] = None
    ) -> Any:
        """
        Get a config value by key with type conversion.

        Returns the parsed Python value based on value_type.
        """
        config = await self.get_config_by_key(key, entity_id)
        if not config:
            return default

        return config.get_value() or default

    async def get_bool(self, key: str, default: bool = False, entity_id: Optional[int] = None) -> bool:
        """Get a boolean config value."""
        value = await self.get_value(key, default, entity_id)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return default

    async def get_int(self, key: str, default: int = 0, entity_id: Optional[int] = None) -> int:
        """Get an integer config value."""
        value = await self.get_value(key, default, entity_id)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    async def get_str(self, key: str, default: str = "", entity_id: Optional[int] = None) -> str:
        """Get a string config value."""
        value = await self.get_value(key, default, entity_id)
        return str(value) if value is not None else default

    async def get_json(
        self,
        key: str,
        default: Any = None,
        entity_id: Optional[int] = None
    ) -> Any:
        """Get a JSON config value."""
        config = await self.get_config_by_key(key, entity_id)
        if not config or not config.value:
            return default
        try:
            return json.loads(config.value)
        except (json.JSONDecodeError, TypeError):
            return default

    # ========================
    # Grouped Access
    # ========================

    async def get_group_configs(self, group: str) -> list[SystemConfig]:
        """Get all configs for a specific group."""
        result = await self.db.execute(
            select(SystemConfig)
            .where(SystemConfig.group == group)
            .order_by(SystemConfig.display_name)
        )
        return list(result.scalars().all())

    async def get_grouped_configs(
        self,
        entity_id: Optional[int] = None
    ) -> list[dict]:
        """
        Get all configs grouped by group name.

        Returns a list of {group, group_name, configs} dicts.
        """
        groups = await self.list_groups()

        result = []
        for group in groups:
            configs = await self.get_group_configs(group.key)

            # For non-global configs, filter by entity
            if entity_id:
                configs = [
                    c for c in configs
                    if c.is_global or c.entity_id == entity_id
                ]

            result.append({
                "group": group.key,
                "group_name": group.name,
                "icon": group.icon,
                "configs": configs
            })

        return result


# ========================
# Default Configurations
# ========================

DEFAULT_CONFIG_GROUPS = [
    {"key": "branding", "name": "Image & Identité", "icon": "building", "display_order": 1},
    {"key": "integrations", "name": "Intégrations", "icon": "link", "display_order": 2},
    {"key": "security", "name": "Sécurité", "icon": "shield", "display_order": 3},
    {"key": "notifications", "name": "Notifications", "icon": "bell", "display_order": 4},
    {"key": "medical", "name": "Paramètres Médicaux", "icon": "stethoscope", "display_order": 5},
    {"key": "billing", "name": "Facturation", "icon": "credit-card", "display_order": 6},
    {"key": "general", "name": "Général", "icon": "cog", "display_order": 99},
]

DEFAULT_CONFIGS = [
    # Branding
    {"key": "brand.name", "group": "branding", "display_name": "Nom de l'application", "value": "PharmAlert", "description": "Nom affiché dans le header et les emails"},
    {"key": "brand.logo_url", "group": "branding", "display_name": "URL du logo", "value": "", "description": "URL du logo de l'établissement"},
    {"key": "brand.favicon_url", "group": "branding", "display_name": "URL du favicon", "value": "", "description": "URL du favicon"},
    {"key": "brand.primary_color", "group": "branding", "display_name": "Couleur primaire", "value": "#3B82F6", "value_type": "color", "description": "Couleur primaire de l'interface"},
    {"key": "brand.secondary_color", "group": "branding", "display_name": "Couleur secondaire", "value": "#10B981", "value_type": "color", "description": "Couleur secondaire de l'interface"},

    # Integrations
    {"key": "integration.minio.endpoint", "group": "integrations", "display_name": "Endpoint MinIO", "value": "", "description": "URL du serveur MinIO/S3"},
    {"key": "integration.minio.access_key", "group": "integrations", "display_name": "Access Key MinIO", "value": "", "is_secret": True},
    {"key": "integration.minio.secret_key", "group": "integrations", "display_name": "Secret Key MinIO", "value": "", "is_secret": True},
    {"key": "integration.minio.bucket", "group": "integrations", "display_name": "Bucket MinIO", "value": "pharmalert"},
    {"key": "integration.fhir.enabled", "group": "integrations", "display_name": "FHIR activé", "value": "true", "value_type": "boolean"},
    {"key": "integration.fhir.base_url", "group": "integrations", "display_name": "URL de base FHIR", "value": ""},

    # Security
    {"key": "security.session_timeout", "group": "security", "display_name": "Timeout session (min)", "value": "480", "value_type": "integer", "description": "Durée de validité du token JWT en minutes"},
    {"key": "security.max_login_attempts", "group": "security", "display_name": "Tentatives max de connexion", "value": "5", "value_type": "integer"},
    {"key": "security.require_mfa", "group": "security", "display_name": "Exiger MFA", "value": "false", "value_type": "boolean"},
    {"key": "security.password_min_length", "group": "security", "display_name": "Longueur min mot de passe", "value": "8", "value_type": "integer"},

    # Notifications
    {"key": "notifications.email.enabled", "group": "notifications", "display_name": "Notifications email", "value": "true", "value_type": "boolean"},
    {"key": "notifications.sms.enabled", "group": "notifications", "display_name": "Notifications SMS", "value": "false", "value_type": "boolean"},
    {"key": "notifications.sms.provider", "group": "notifications", "display_name": "Provider SMS", "value": "infobip", "choices": '["infobip", "twilio", "ovh"]'},
    {"key": "notifications.whatsapp.enabled", "group": "notifications", "display_name": "Notifications WhatsApp", "value": "false", "value_type": "boolean"},

    # Medical
    {"key": "medical.auto_check_interactions", "group": "medical", "display_name": "Vérification auto des interactions", "value": "true", "value_type": "boolean"},
    {"key": "medical.interaction_severity_threshold", "group": "medical", "display_name": "Seuil de sévérité des interactions", "value": "moderate", "choices": '["minor", "moderate", "major", "contraindicated"]'},
    {"key": "medical.require_allergy_check", "group": "medical", "display_name": "Vérification allergies obligatoire", "value": "true", "value_type": "boolean"},
    {"key": "medical.allow_interaction_override", "group": "medical", "display_name": "Permettre le contournement des interactions", "value": "true", "value_type": "boolean"},
    {"key": "medical.override_requires_justification", "group": "medical", "display_name": "Justification obligatoire pour contournement", "value": "true", "value_type": "boolean"},

    # Billing
    {"key": "billing.invoice_prefix", "group": "billing", "display_name": "Préfixe facture", "value": "INV"},
    {"key": "billing.currency", "group": "billing", "display_name": "Devise", "value": "XOF"},
    {"key": "billing.deposit_required", "group": "billing", "display_name": "Acompte obligatoire", "value": "false", "value_type": "boolean"},
    {"key": "billing.deposit_minimum", "group": "billing", "display_name": "Acompte minimum (%)", "value": "20", "value_type": "integer"},

    # General
    {"key": "general.language", "group": "general", "display_name": "Langue par défaut", "value": "fr"},
    {"key": "general.timezone", "group": "general", "display_name": "Fuseau horaire", "value": "Africa/Lome"},
    {"key": "general.date_format", "group": "general", "display_name": "Format de date", "value": "DD/MM/YYYY"},
    {"key": "general.records_per_page", "group": "general", "display_name": "Enregistrements par page", "value": "20", "value_type": "integer"},
    {"key": "general.maintenance_mode", "group": "general", "display_name": "Mode maintenance", "value": "false", "value_type": "boolean"},
]


async def seed_default_configs(db: AsyncSession) -> None:
    """
    Seed default config groups and configs if they don't exist.

    Call this on startup or in a migration.
    """
    from sqlalchemy import select

    # Seed groups
    for group_data in DEFAULT_CONFIG_GROUPS:
        result = await db.execute(
            select(ConfigGroup).where(ConfigGroup.key == group_data["key"])
        )
        if result.scalar_one_or_none() is None:
            db.add(ConfigGroup(**group_data))

    await db.flush()

    # Seed configs
    for config_data in DEFAULT_CONFIGS:
        key = config_data.pop("key")
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.key == key)
        )
        if result.scalar_one_or_none() is None:
            db.add(SystemConfig(key=key, **config_data))

    await db.commit()