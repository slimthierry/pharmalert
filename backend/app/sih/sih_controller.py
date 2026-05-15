"""
SIH Sync Controller — Endpoints REST pour la synchronisation Odoo Likmed.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import AsyncSessionLocal, engine
from app.config.settings import settings
from app.auth.dependencies import get_current_user
from app.models.user_models import User
from app.models.entity import Entity, EntityUserAssignment
from app.sih.sih_sync_service import SIHClient, SIHSyncService
from app.sih.dto import (
    SIHLoginResponse, SIHTokenData,
    SIHSyncStatus, SIHLoginRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["SIH Sync"])


# ─── Dependencies ─────────────────────────────────────────────────────────────

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_entity(
    entity_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Entity:
    """
    Récupère l'entity demandée ou celle par défaut de l'utilisateur.
    """
    if entity_id:
        # Vérifier que l'utilisateur a accès à cette entity
        assignment = await db.execute(
            select(EntityUserAssignment).where(
                EntityUserAssignment.user_id == current_user.id,
                EntityUserAssignment.entity_id == entity_id
            )
        )
        if not assignment.scalar_one_or_none():
            raise HTTPException(403, "Accès refusé à cette entité")
        entity = await db.get(Entity, entity_id)
        if not entity:
            raise HTTPException(404, "Entité non trouvée")
        return entity

    # Récupérer l'entity par défaut de l'utilisateur
    assignment = await db.execute(
        select(EntityUserAssignment).where(
            EntityUserAssignment.user_id == current_user.id,
            EntityUserAssignment.is_default == True
        )
    )
    default = assignment.scalar_one_or_none()
    if not default:
        raise HTTPException(400, "Aucune entité par défaut. Spécifiez entity_id.")
    entity = await db.get(Entity, default.entity_id)
    if not entity:
        raise HTTPException(404, "Entité par défaut introuvable")
    return entity


def get_sih_client(entity: Entity) -> SIHClient:
    """
    Crée un client SIH pour l'entity donnée.
    Utilise les configs SIH de l'entity.
    """
    # Priorité: configs de l'entity > settings globaux
    sih_url = entity.sih_config.get("url") if entity.sih_config else None
    sih_db = entity.sih_config.get("db") if entity.sih_config else None
    sih_username = entity.sih_config.get("username") if entity.sih_config else None
    sih_password = entity.sih_config.get("password") if entity.sih_config else None

    if not sih_url:
        sih_url = settings.SIH_URL
    if not sih_db:
        sih_db = settings.SIH_DB
    if not sih_username:
        sih_username = settings.SIH_USERNAME
    if not sih_password:
        sih_password = settings.SIH_PASSWORD

    return SIHClient(
        url=sih_url,
        db=sih_db,
        username=sih_username,
        password=sih_password,
        entity_id=entity.id
    )


# ─── Authentication ──────────────────────────────────────────────────────────

@router.get("/status", response_model=SIHSyncStatus)
async def sih_status(
    entity: Entity = Depends(get_current_entity)
):
    """
    Retourne le statut de la connexion SIH (connectivité uniquement).
    Ne stocke pas le token — appelle juste la méthode de test.
    """
    client = get_sih_client(entity)
    connected = client.is_connected()

    # Lecture des stats de sync depuis la DB si disponibles
    async with AsyncSessionLocal() as session:
        from sqlalchemy import func
        from app.models.patient_models import Patient
        from app.models.medication_models import Medication
        from app.models.prescription_models import Prescription

        patients_count = await session.scalar(
            select(func.count(Patient.id)).where(Patient.entity_id == entity.id)
        ) or 0
        drugs_count = await session.scalar(
            select(func.count(Medication.id)).where(Medication.entity_id == entity.id)
        ) or 0
        orders_count = await session.scalar(
            select(func.count(Prescription.id)).where(Prescription.entity_id == entity.id)
        ) or 0

    return SIHSyncStatus(
        connected=connected,
        last_sync=entity.last_sih_sync,
        patients_count=patients_count,
        drugs_count=drugs_count,
        orders_count=orders_count,
        error=None if connected else "Impossible de se connecter au SIH"
    )


@router.post("/connect", response_model=SIHLoginResponse)
async def sih_connect(
    request: Optional[SIHLoginRequest] = None,
    entity: Entity = Depends(get_current_entity)
):
    """
    Teste la connexion au SIH Odoo avec les credentials configurés.
    Optionnellement, peut accepter des credentials temporaires en body.
    """
    client = get_sih_client(entity)

    # Override avec credentials en body si fournis
    if request and request.login and request.password:
        client.username = request.login
        client.password = request.password

    result = client.authenticate()

    if not result.success:
        raise HTTPException(401, result.error or {"message": "Connexion échouée"})

    # Stocker le token en session (optionnel, XML-RPC ne stocke pas de token Bearer)
    # Le token XML-RPC est basé sur l'uid, pas un JWT
    return result


# ─── Sync Endpoints ─────────────────────────────────────────────────────────

@router.post("/sync/all")
async def sih_sync_all(
    entity: Entity = Depends(get_current_entity)
):
    """
    Lance une synchronisation complète depuis le SIH.
   同步:
    1. Patients (likmed.patient.base)
    2. Médicaments (likmed.drug)
    3. Ordonnances (likmed.order)
    4. Allergies (likmed.patient.allergy)
    """
    client = get_sih_client(entity)

    # Vérifier la connexion
    if not client.is_connected():
        raise HTTPException(503, "SIH non joignable. Vérifiez la configuration.")

    # Vérifier que les credentials sont configurés
    if not client.username or not client.password:
        raise HTTPException(400, "Credentials SIH non configurés pour cette entité.")

    # L'authentification n'est pas nécessaire pour XML-RPC read-only
    # mais on vérifie quand même que la DB est accessible
    try:
        client.authenticate()
    except Exception as e:
        raise HTTPException(503, f"Erreur de connexion SIH: {e}")

    service = SIHSyncService(client, entity.id)
    stats = await service.sync_all()

    # Mettre à jour la date de dernière sync sur l'entity
    async with AsyncSessionLocal() as session:
        entity_db = await session.get(Entity, entity.id)
        if entity_db:
            entity_db.last_sih_sync = datetime.utcnow()
            await session.commit()

    if stats.get("error"):
        raise HTTPException(500, stats["error"])

    return {
        "success": True,
        "message": "Synchronisation terminée",
        "stats": {
            "patients_synced": stats.get("patients_synced", 0),
            "drugs_synced": stats.get("drugs_synced", 0),
            "orders_synced": stats.get("orders_synced", 0),
            "allergies_synced": stats.get("allergies_synced", 0),
            "last_sync": stats.get("last_sync")
        }
    }


@router.post("/sync/patients")
async def sih_sync_patients(
    entity: Entity = Depends(get_current_entity)
):
    """Synchronise uniquement les patients depuis le SIH."""
    client = get_sih_client(entity)
    if not client.is_connected():
        raise HTTPException(503, "SIH non joignable")

    client.authenticate()
    service = SIHSyncService(client, entity.id)
    count = await service._sync_patients()

    return {"success": True, "patients_synced": count}


@router.post("/sync/drugs")
async def sih_sync_drugs(
    entity: Entity = Depends(get_current_entity)
):
    """Synchronise uniquement les médicaments depuis le SIH."""
    client = get_sih_client(entity)
    if not client.is_connected():
        raise HTTPException(503, "SIH non joignable")

    client.authenticate()
    service = SIHSyncService(client, entity.id)
    count = await service._sync_drugs()

    return {"success": True, "drugs_synced": count}


@router.post("/sync/orders")
async def sih_sync_orders(
    entity: Entity = Depends(get_current_entity)
):
    """Synchronise uniquement les ordonnances depuis le SIH."""
    client = get_sih_client(entity)
    if not client.is_connected():
        raise HTTPException(503, "SIH non joignable")

    client.authenticate()
    service = SIHSyncService(client, entity.id)
    count = await service._sync_prescriptions()

    return {"success": True, "orders_synced": count}


@router.post("/sync/allergies")
async def sih_sync_allergies(
    entity: Entity = Depends(get_current_entity)
):
    """Synchronise uniquement les allergies depuis le SIH."""
    client = get_sih_client(entity)
    if not client.is_connected():
        raise HTTPException(503, "SIH non joignable")

    client.authenticate()
    service = SIHSyncService(client, entity.id)
    count = await service._sync_allergies()

    return {"success": True, "allergies_synced": count}


# ─── Browse SIH Data (Read-only, without saving) ─────────────────────────────

@router.get("/patients")
async def sih_browse_patients(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    entity: Entity = Depends(get_current_entity)
):
    """
    Lit les patients depuis le SIH (lecture seule, sans synchroniser).
    Utile pour prévisualiser les données avant sync.
    """
    client = get_sih_client(entity)
    if not client.is_connected():
        raise HTTPException(503, "SIH non joignable")

    auth = client.authenticate()
    if not auth.success:
        raise HTTPException(401, f"Échec auth SIH: {auth.error}")
    patients = client.get_patients(offset=offset, limit=limit)
    total = client.get_patient_count()

    return {
        "patients": patients,
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.get("/drugs")
async def sih_browse_drugs(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    entity: Entity = Depends(get_current_entity)
):
    """
    Lit les médicaments depuis le SIH (lecture seule, sans synchroniser).
    """
    client = get_sih_client(entity)
    if not client.is_connected():
        raise HTTPException(503, "SIH non joignable")

    auth = client.authenticate()
    if not auth.success:
        raise HTTPException(401, f"Échec auth SIH: {auth.error}")
    drugs = client.get_drugs(offset=offset, limit=limit)
    total = client.get_drug_count()

    return {
        "drugs": drugs,
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.get("/orders")
async def sih_browse_orders(
    patient_id: Optional[int] = Query(None),
    state: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    entity: Entity = Depends(get_current_entity)
):
    """
    Lit les ordonnances depuis le SIH (lecture seule, sans synchroniser).
    """
    client = get_sih_client(entity)
    if not client.is_connected():
        raise HTTPException(503, "SIH non joignable")

    auth = client.authenticate()
    if not auth.success:
        raise HTTPException(401, f"Échec auth SIH: {auth.error}")
    orders = client.get_orders(
        patient_id=patient_id,
        state=state,
        date_from=date_from,
        offset=offset,
        limit=limit
    )

    return {
        "orders": orders,
        "offset": offset,
        "limit": limit
    }


# ─── Configure SIH for Entity ───────────────────────────────────────────────

@router.post("/configure")
async def sih_configure(
    sih_url: str = Query(..., description="URL d'Odoo (ex: http://localhost:4430)"),
    sih_db: str = Query(..., description="Nom de la base Odoo (ex: likmed_db)"),
    sih_username: str = Query(..., description="Login Odoo (ex: admin)"),
    sih_password: str = Query(..., description="Mot de passe Odoo"),
    entity: Entity = Depends(get_current_entity),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure les credentials SIH pour une entity.
    Les credentials sont stockés dans entity.sih_config (JSONB).
    """
    # Tester la connexion avant d'enregistrer
    test_client = SIHClient(
        url=sih_url,
        db=sih_db,
        username=sih_username,
        password=sih_password,
        entity_id=entity.id
    )

    auth_result = test_client.authenticate()
    if not auth_result.success:
        raise HTTPException(401, f"Connexion SIH échouée: {auth_result.error}")

    # Enregistrer les configs dans l'entity
    entity_db = await db.get(Entity, entity.id)
    if not entity_db:
        raise HTTPException(404, "Entité non trouvée")

    entity_db.sih_config = {
        "url": sih_url,
        "db": sih_db,
        "username": sih_username,
        "password": sih_password  # En production, chiffrer ce champ
    }
    await db.commit()

    return {
        "success": True,
        "message": "Configuration SIH enregistrée",
        "entity_id": entity.id,
        "entity_name": entity_db.name
    }


@router.get("/configure")
async def sih_get_config(
    entity: Entity = Depends(get_current_entity)
):
    """
    Retourne la configuration SIH actuelle (sans le mot de passe).
    """
    config = entity.sih_config or {}
    safe_config = {
        "url": config.get("url", ""),
        "db": config.get("db", ""),
        "username": config.get("username", ""),
        "password_set": bool(config.get("password"))
    }
    return safe_config