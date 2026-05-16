"""
SIH Sync Service — Synchronise les données depuis Odoo Likmed vers PharmAlert.
Utilise XML-RPC pour communiquer avec l'API Odoo.
"""

import logging
from datetime import datetime, date
from typing import Optional, List
import xmlrpc.client

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import AsyncSessionLocal
from app.models.patient_models import Patient
from app.models.allergy_models import PatientAllergy as Allergy
from app.models.medication_models import Medication
from app.models.prescription_models import Prescription
from app.models.entity import Entity
from app.sih.dto import (
    SIHLoginResponse, SIHPatient, SIHDrug, SIHOrder,
    SIHOrderLine, SIHAllergy, SIHSyncStatus, SIHToken
)

logger = logging.getLogger(__name__)

# ─── XML-RPC Client ───────────────────────────────────────────────────────────

class SIHClient:
    """
    Client XML-RPC pour communiquer avec Odoo Likmed.
    """

    def __init__(
        self,
        url: str,
        db: str,
        username: str,
        password: str,
        entity_id: int
    ):
        self.url = url.rstrip("/")
        self.db = db
        self.username = username
        self.password = password
        self.entity_id = entity_id
        self._uid: Optional[int] = None
        self._token: Optional[str] = None
        self._models = None
        self._common = None

    @property
    def common(self) -> xmlrpc.client.ServerProxy:
        if self._common is None:
            self._common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        return self._common

    @property
    def models(self) -> xmlrpc.client.ServerProxy:
        if self._models is None:
            self._models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        return self._models

    def authenticate(self) -> SIHLoginResponse:
        """
        Authentifie avec Odoo via XML-RPC et retourne le token.
        """
        try:
            uid = self.common.authenticate(self.db, self.username, self.password, {})
            if not uid:
                return SIHLoginResponse(
                    success=False,
                    error={"code": "auth_failed", "message": "Identifiants invalides"}
                )
            self._uid = uid

            # Lecture des permissions (groups)
            groups = self.models.execute_kw(
                self.db, uid, self.password,
                'res.users', 'read',
                [uid],
                {'fields': ['groups_id', 'name', 'login']}
            )[0]

            perms = []
            if groups:
                perms = [str(g) for g in groups.get('groups_id', [])]

            self._token = f"xmlrpc_{uid}_{datetime.now().timestamp()}"

            return SIHLoginResponse(
                success=True,
                data={
                    "token": self._token,
                    "uid": uid,
                    "user": groups.get('name', ''),
                    "session_id": str(uid),
                    "permissions": perms
                }
            )
        except Exception as e:
            logger.error(f"SIH Auth error: {e}")
            return SIHLoginResponse(
                success=False,
                error={"code": "connection_error", "message": str(e)}
            )

    def _call(self, model: str, method: str, *args, **kwargs):
        """Appelle une méthode Odoo via XML-RPC."""
        if self._uid is None:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        return self.models.execute_kw(self.db, self._uid, self.password, model, method, *args, **kwargs)

    def is_connected(self) -> bool:
        """Teste si la connexion Odoo est active."""
        try:
            self.common.version()
            return True
        except Exception:
            return False

    # ─── Patients ─────────────────────────────────────────────────────────────

    def get_patients(self, offset: int = 0, limit: int = 100) -> List[dict]:
        """
        Récupère les patients depuis Odoo.
        """
        try:
            return self._call('likmed.patient.base', 'search_read', [], {
                'offset': offset,
                'limit': limit,
                'order': 'id desc',
                'fields': [
                    'id', 'reference', 'name', 'last_name', 'first_name',
                    'gender', 'birth_date', 'phone', 'email', 'address',
                    'is_hospitalized', 'patient_insurance_id', 'active'
                ]
            }) or []
        except Exception as e:
            logger.error(f"Error fetching patients: {e}")
            return []

    def get_patient_count(self) -> int:
        """Retourne le nombre total de patients."""
        try:
            ids = self._call('likmed.patient.base', 'search_count', [[('active', '=', True)]])
            return ids or 0
        except Exception:
            return 0

    # ─── Drugs / Medications ───────────────────────────────────────────────────

    def get_drugs(self, offset: int = 0, limit: int = 200) -> List[dict]:
        """
        Récupère les médicaments depuis Odoo.
        """
        try:
            return self._call('likmed.drug', 'search_read', [], {
                'offset': offset,
                'limit': limit,
                'order': 'name asc',
                'fields': [
                    'id', 'name', 'code', 'sale_price', 'purchase_price',
                    'amm_number', 'dosage', 'manufacturer_id',
                    'classification_drug_type', 'classification_form',
                    'dci_id', 'current_stock', 'stock_status', 'active'
                ]
            }) or []
        except Exception as e:
            logger.error(f"Error fetching drugs: {e}")
            return []

    def get_drug_count(self) -> int:
        try:
            return self._call('likmed.drug', 'search_count', [[('active', '=', True)]]) or 0
        except Exception:
            return 0

    # ─── Orders / Prescriptions ───────────────────────────────────────────────

    def get_orders(
        self,
        patient_id: Optional[int] = None,
        state: Optional[str] = None,
        date_from: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """
        Récupère les ordonnances depuis Odoo.
        """
        try:
            domain = []
            if patient_id:
                domain.append(('patient_id', '=', patient_id))
            if state:
                domain.append(('state', '=', state))
            if date_from:
                domain.append(('date', '>=', date_from))

            return self._call('likmed.order', 'search_read', [domain], {
                'offset': offset,
                'limit': limit,
                'order': 'date desc',
                'fields': [
                    'id', 'name', 'date', 'patient_id',
                    'service_id', 'state', 'notes', 'order_line_ids',
                    'medical_person_id', 'order_type'
                ]
            }) or []
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []

    def get_order_lines(self, line_ids: List[int]) -> List[dict]:
        """
        Récupère les lignes d'ordonnance depuis Odoo.
        """
        if not line_ids:
            return []
        try:
            return self._call('likmed.order.line', 'read', [line_ids], {
                'fields': [
                    'id', 'order_id', 'product_id', 'name',
                    'quantity', 'dosage', 'dose_per_take', 'dose_unit',
                    'frequency', 'scheduled_times', 'route',
                    'start_date', 'end_date', 'duration',
                    'meal_relation', 'dosage_instructions'
                ]
            }) or []
        except Exception as e:
            logger.error(f"Error fetching order lines: {e}")
            return []

    def get_order_count(self, date_from: Optional[str] = None) -> int:
        try:
            domain = [['state', 'in', ('draft', 'done')]]
            if date_from:
                domain.append(('date', '>=', date_from))
            return self._call('likmed.order', 'search_count', [domain]) or 0
        except Exception:
            return 0

    # ─── Allergies ─────────────────────────────────────────────────────────────

    def get_patient_allergies(self, patient_id: int) -> List[dict]:
        """
        Récupère les allergies d'un patient depuis Odoo.
        """
        try:
            return self._call('likmed.patient.allergy', 'search_read', [
                [('patient_id', '=', patient_id)]
            ], {
                'fields': ['id', 'patient_id', 'allergy_id', 'date', 'note']
            }) or []
        except Exception as e:
            logger.error(f"Error fetching allergies for patient {patient_id}: {e}")
            return []

    def get_all_patients_allergies(self, limit: int = 1000) -> List[dict]:
        """Récupère toutes les allergies de tous les patients."""
        try:
            return self._call('likmed.patient.allergy', 'search_read', [], {
                'limit': limit,
                'fields': ['id', 'patient_id', 'allergy_id', 'date', 'note']
            }) or []
        except Exception as e:
            logger.error(f"Error fetching all allergies: {e}")
            return []

    # ─── DCI (Active Principle) ────────────────────────────────────────────────

    def get_dci_names(self, dci_ids: List[int]) -> dict:
        """Récupère les noms de DCI (principes actifs)."""
        if not dci_ids:
            return {}
        try:
            records = self._call('likmed.drug.dci', 'read', [dci_ids], {
                'fields': ['id', 'name']
            }) or []
            return {r['id']: r['name'] for r in records}
        except Exception:
            return {}


# ─── Sync Service ─────────────────────────────────────────────────────────────

class SIHSyncService:
    """
    Service qui synchronise les données d'Odoo Likmed vers la base PharmAlert.
    """

    def __init__(self, client: SIHClient, entity_id: int):
        self.client = client
        self.entity_id = entity_id
        self._sync_stats = {
            "patients_synced": 0,
            "drugs_synced": 0,
            "orders_synced": 0,
            "allergies_synced": 0,
            "last_sync": None,
            "error": None
        }

    @property
    def sync_stats(self) -> dict:
        return self._sync_stats.copy()

    async def _get_session(self) -> AsyncSession:
        return AsyncSessionLocal()

    async def sync_all(self) -> dict:
        """
        Synchronise toutes les données (patients, médicaments, ordonnances, allergies).
        """
        self._sync_stats["error"] = None
        try:
            logger.info(f"Starting full SIH sync for entity {self.entity_id}")

            # 1. Sync patients
            synced_p = await self._sync_patients()
            self._sync_stats["patients_synced"] = synced_p
            logger.info(f"Patients synced: {synced_p}")

            # 2. Sync drugs/medications
            synced_d = await self._sync_drugs()
            self._sync_stats["drugs_synced"] = synced_d
            logger.info(f"Drugs synced: {synced_d}")

            # 3. Sync prescriptions
            synced_o = await self._sync_prescriptions()
            self._sync_stats["orders_synced"] = synced_o
            logger.info(f"Orders synced: {synced_o}")

            # 4. Sync allergies
            synced_a = await self._sync_allergies()
            self._sync_stats["allergies_synced"] = synced_a
            logger.info(f"Allergies synced: {synced_a}")

            self._sync_stats["last_sync"] = datetime.utcnow()

        except Exception as e:
            logger.error(f"SIH sync error: {e}")
            self._sync_stats["error"] = str(e)

        return self._sync_stats

    async def _sync_patients(self) -> int:
        """
        Synchronise les patients depuis Odoo.
        Les données patients du SIH sont stockées comme référence externe.
        PharmAlert utilise son propre ID patient (IPP).
        """
        session = await self._get_session()
        count = 0

        try:
            # Récupérer tous les patients par lots de 100
            offset = 0
            batch_size = 100

            while True:
                patients_data = self.client.get_patients(offset=offset, limit=batch_size)
                if not patients_data:
                    break

                for p in patients_data:
                    try:
                        # Vérifier si le patient existe déjà (par référence externe SIH)
                        existing = await session.execute(
                            select(Patient).where(
                                Patient.entity_id == self.entity_id,
                                Patient.sih_reference == str(p['id'])
                            )
                        )
                        patient = existing.scalar_one_or_none()

                        # Parser la date de naissance
                        birth_date = None
                        if p.get('birth_date'):
                            try:
                                birth_date = datetime.strptime(str(p['birth_date']), '%Y-%m-%d').date()
                            except Exception:
                                birth_date = None

                        patient_name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
                        if not patient_name or patient_name == " ":
                            patient_name = p.get('name', f"Patient {p['id']}")

                        gender_map = {'male': 'M', 'female': 'F', 'M': 'M', 'F': 'F'}
                        gender = gender_map.get(p.get('gender', ''), 'M')

                        if patient is None:
                            ins_id = p.get('patient_insurance_id')
                            if isinstance(ins_id, (list, tuple)):
                                ins_id = ins_id[0] if ins_id else None
                            has_ins = bool(ins_id)
                            ins_num = str(ins_id) if ins_id else None

                            # Créer un nouveau patient PharmAlert
                            patient = Patient(
                                entity_id=self.entity_id,
                                ipp=f"SIH-{p['id']}",
                                first_name=p.get('first_name') or '',
                                last_name=p.get('last_name') or '',
                                birth_date=birth_date,
                                gender=gender,
                                phone=p.get('phone') or None,
                                email=p.get('email') or None,
                                address=p.get('address') or None,
                                is_hospitalized=p.get('is_hospitalized', False),
                                has_insurance=has_ins,
                                insurance_number=ins_num,
                                sih_reference=str(p['id']),
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            session.add(patient)
                        else:
                            patient.first_name = p.get('first_name') or patient.first_name
                            patient.last_name = p.get('last_name') or patient.last_name
                            if birth_date:
                                patient.birth_date = birth_date
                            if p.get('phone'):
                                patient.phone = p.get('phone')
                            if p.get('email'):
                                patient.email = p.get('email')
                            patient.updated_at = datetime.utcnow()

                        count += 1

                    except Exception as e:
                        logger.warning(f"Error syncing patient {p.get('id')}: {e}")
                        await session.rollback()
                        continue

                offset += batch_size
                await session.commit()

                if len(patients_data) < batch_size:
                    break

        finally:
            await session.close()

        return count

    async def _sync_drugs(self) -> int:
        """
        Synchronise les médicaments depuis Odoo.
        Map likmed.drug → Medication dans PharmAlert.
        """
        session = await self._get_session()
        count = 0

        try:
            # Récupérer les DCI (principes actifs) pour le mapping
            all_drugs = self.client.get_drugs(offset=0, limit=1000)
            dci_ids = list(set(d.get('dci_id', [0])[0] if isinstance(d.get('dci_id'), (list, tuple)) else d.get('dci_id', 0) for d in all_drugs))
            dci_names = self.client.get_dci_names([i for i in dci_ids if i])

            for d in all_drugs:
                try:
                    # Vérifier si le médicament existe déjà
                    existing = await session.execute(
                        select(Medication).where(
                            Medication.entity_id == self.entity_id,
                            Medication.sih_reference == str(d['id'])
                        )
                    )
                    medication = existing.scalar_one_or_none()

                    # Extraire le nom DCI
                    dci_id = d.get('dci_id')
                    if isinstance(dci_id, (list, tuple)):
                        dci_id = dci_id[0] if dci_id else 0
                    active_principle = dci_names.get(dci_id)

                    # Type de médicament
                    drug_type_id = d.get('classification_drug_type')
                    if isinstance(drug_type_id, (list, tuple)):
                        drug_type_id = drug_type_id[0] if drug_type_id else None

                    if medication is None:
                        medication = Medication(
                            entity_id=self.entity_id,
                            name=d.get('name', '') or '',
                            atc_code=d.get('code') or None,
                            atc_code_original=d.get('amm_number') or None,
                            active_principle=active_principle,
                            stock_quantity=float(d.get('current_stock', 0)) or 0.0,
                            is_controlled=(d.get('stock_status') == 'out_of_stock'),
                            sih_reference=str(d['id']),
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        session.add(medication)
                    else:
                        medication.name = d.get('name', '') or medication.name
                        medication.stock_quantity = float(d.get('current_stock', 0)) or 0.0
                        medication.updated_at = datetime.utcnow()

                    count += 1

                except Exception as e:
                    logger.warning(f"Error syncing drug {d.get('id')}: {e}")
                    await session.rollback()
                    continue

            await session.commit()

        finally:
            await session.close()

        return count

    async def _sync_prescriptions(self) -> int:
        """
        Synchronise les ordonnances depuis Odoo.
        Map likmed.order → Prescription dans PharmAlert.
        Ne sincronise que les prescriptions des 30 derniers jours.
        """
        session = await self._get_session()
        count = 0

        try:
            # Sync all orders (no date filter - sync everything)
            offset = 0
            batch_size = 50

            while True:
                orders = self.client.get_orders(
                    offset=offset,
                    limit=batch_size
                )
                if not orders:
                    break

                for order in orders:
                    try:
                        # Vérifier si la prescription existe déjà
                        existing = await session.execute(
                            select(Prescription).where(
                                Prescription.entity_id == self.entity_id,
                                Prescription.sih_reference == str(order['id'])
                            )
                        )
                        prescription = existing.scalar_one_or_none()

                        # Récupérer les lignes d'ordonnance
                        line_ids = order.get('order_line_ids', [])
                        order_lines = self.client.get_order_lines(line_ids) if line_ids else []

                        # Trouver le patient PharmAlert correspondant
                        patient_ipp = None
                        if order.get('patient_id'):
                            pid = order['patient_id'][0] if isinstance(order['patient_id'], (list, tuple)) else order['patient_id']
                            patient_result = await session.execute(
                                select(Patient).where(
                                    Patient.entity_id == self.entity_id,
                                    Patient.sih_reference == str(pid)
                                )
                            )
                            patient = patient_result.scalar_one_or_none()
                            if patient:
                                patient_ipp = patient.ipp

                        # Parser la date
                        order_date = datetime.now()
                        if order.get('date'):
                            try:
                                if 'T' in str(order['date']):
                                    order_date = datetime.fromisoformat(str(order['date']).replace('Z', '+00:00'))
                                else:
                                    order_date = datetime.strptime(str(order['date']), '%Y-%m-%d %H:%M:%S')
                            except Exception:
                                order_date = datetime.now()

                        state_map = {
                            'draft': 'pending',
                            'done': 'validated',
                            'invoiced': 'validated',
                            'cancelled': 'rejected'
                        }
                        prescription_state = state_map.get(order.get('state', 'pending'), 'pending')

                        # Construire la fréquence principale
                        frequencies = list(set(l.get('frequency') for l in order_lines if l.get('frequency')))
                        frequency = frequencies[0] if frequencies else None

                        # Construire les instructions
                        instructions = []
                        for line in order_lines:
                            if line.get('dosage_instructions'):
                                instructions.append(f"{line.get('drug_name', '')}: {line.get('dosage_instructions', '')}")
                        notes = order.get('notes', '') or ('\n'.join(instructions) if instructions else None)

                        if prescription is None:
                            mp_id = order.get('medical_person_id')
                            if isinstance(mp_id, (list, tuple)):
                                prescribed = mp_id[1] if len(mp_id) > 1 else None
                            else:
                                prescribed = None

                            prescription = Prescription(
                                entity_id=self.entity_id,
                                patient_ipp=patient_ipp or f"SIH-{order.get('patient_id', [[0]])[0]}",
                                patient_name=order.get('patient_id', [None, ''])[1] if isinstance(order.get('patient_id'), (list, tuple)) else None,
                                frequency=frequency,
                                status=prescription_state,
                                prescribed_by=prescribed,
                                sih_reference=str(order['id']),
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            session.add(prescription)
                        else:
                            prescription.status = prescription_state
                            prescription.updated_at = datetime.utcnow()

                        count += 1

                    except Exception as e:
                        logger.warning(f"Error syncing order {order.get('id')}: {e}")
                        await session.rollback()
                        continue

                offset += batch_size
                await session.commit()

                if len(orders) < batch_size:
                    break

        finally:
            await session.close()

        return count

    async def _sync_allergies(self) -> int:
        """
        Synchronise les allergies depuis Odoo.
        Map likmed.patient.allergy → Allergy dans PharmAlert.
        """
        session = await self._get_session()
        count = 0

        try:
            allergies_data = self.client.get_all_patients_allergies(limit=5000)

            for allergy_data in allergies_data:
                try:
                    # Trouver le patient PharmAlert
                    patient_id_raw = allergy_data.get('patient_id')
                    if isinstance(patient_id_raw, (list, tuple)):
                        patient_sih_id = str(patient_id_raw[0])
                    else:
                        patient_sih_id = str(patient_id_raw)

                    patient_result = await session.execute(
                        select(Patient).where(
                            Patient.entity_id == self.entity_id,
                            Patient.sih_reference == patient_sih_id
                        )
                    )
                    patient = patient_result.scalar_one_or_none()
                    if not patient:
                        continue

                    # Récupérer le nom de l'allergie
                    allergy_id_raw = allergy_data.get('allergy_id')
                    if isinstance(allergy_id_raw, (list, tuple)):
                        allergy_id = allergy_id_raw[0]
                        allergy_name = allergy_id_raw[1] if len(allergy_id_raw) > 1 else "Allergie inconnue"
                    else:
                        allergy_id = allergy_id_raw
                        allergy_name = "Allergie"

                    # Vérifier si l'allergie existe déjà
                    existing = await session.execute(
                        select(Allergy).where(
                            Allergy.entity_id == self.entity_id,
                            Allergy.patient_id == patient.id,
                            Allergy.sih_reference == str(allergy_data['id'])
                        )
                    )
                    existing_allergy = existing.scalar_one_or_none()

                    if existing_allergy is None:
                        allergy = Allergy(
                            entity_id=self.entity_id,
                            patient_id=patient.id,
                            allergen_type='medicament',
                            allergen_name=allergy_name,
                            severity='major',
                            reaction_type=allergy_data.get('note') or 'OTHER',
                            sih_reference=str(allergy_data['id']),
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        session.add(allergy)
                        count += 1

                except Exception as e:
                    logger.warning(f"Error syncing allergy {allergy_data.get('id')}: {e}")
                    await session.rollback()
                    continue

            await session.commit()

        finally:
            await session.close()

        return count