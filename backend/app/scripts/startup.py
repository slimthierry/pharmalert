"""Startup script: create tables and seed data, then run uvicorn."""

import asyncio
import bcrypt
import uvicorn

from app.config.database import engine, AsyncSessionLocal
from app.models import Base
from app.models.user_models import User, UserRole


async def init() -> None:
    """Create tables and seed data."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        from app.models.medication_models import Medication
        from app.models.interaction_models import Interaction
        from app.models.prescription_models import Prescription
        from app.models.allergy_models import PatientAllergy

        # --- Admin ---
        result = await session.execute(
            select(User).where(User.email == 'admin@pharmalert.com')
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.hashed_password = bcrypt.hashpw(
                'admin123'.encode(), bcrypt.gensalt()
            ).decode()
            await session.commit()
            print('Admin updated: admin@pharmalert.com / admin123')
        else:
            hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
            admin = User(
                email='admin@pharmalert.com',
                name='Admin',
                hashed_password=hashed,
                role=UserRole.ADMIN,
            )
            session.add(admin)
            await session.commit()
            print('Admin created: admin@pharmalert.com / admin123')

        # --- Seed only if empty ---
        meds_result = await session.execute(select(Medication))
        if meds_result.scalars().first() is not None:
            print('Data already seeded, skipping.')
            return

        # --- Médicaments ---
        from app.models.medication_models import MedicationForm
        meds = [
            Medication(name='Amoxicilline', dci='Amoxicilline', atc_code='J01CA04', dosage_unit='500mg', form=MedicationForm.TABLET),
            Medication(name='Warfarine', dci='Warfarine sodique', atc_code='B01AA03', dosage_unit='5mg', form=MedicationForm.TABLET),
            Medication(name='Aspirine', dci='Acide acétylsalicylique', atc_code='N02BA01', dosage_unit='500mg', form=MedicationForm.TABLET),
            Medication(name='Ibuprofène', dci='Ibuprofène', atc_code='M01AE01', dosage_unit='400mg', form=MedicationForm.TABLET),
            Medication(name='Métoprolol', dci='Métoprolol succinate', atc_code='C07AB02', dosage_unit='50mg', form=MedicationForm.TABLET),
            Medication(name='Lisinopril', dci='Lisinopril', atc_code='C09AA03', dosage_unit='10mg', form=MedicationForm.TABLET),
            Medication(name='Oméprazole', dci='Oméprazole', atc_code='A02BC01', dosage_unit='20mg', form=MedicationForm.CAPSULE),
            Medication(name='Paracétamol', dci='Paracétamol', atc_code='N02BE01', dosage_unit='1000mg', form=MedicationForm.TABLET),
            Medication(name='Amlodipine', dci='Amlodipine besylate', atc_code='C08CA01', dosage_unit='5mg', form=MedicationForm.TABLET),
            Medication(name='Simvastatine', dci='Simvastatine', atc_code='C10AA01', dosage_unit='20mg', form=MedicationForm.TABLET),
        ]
        session.add_all(meds)
        await session.flush()
        print(f'{len(meds)} médicaments créés')

        from app.models.interaction_models import InteractionSeverity
        interactions = [
            Interaction(
                medication_a_id=meds[4].id, medication_b_id=meds[9].id,
                severity=InteractionSeverity.MAJOR,
                clinical_effect='Risque de myopathie/rhabdomyolyse',
                recommendation='Surveillance CK, ajustez dose simvastatine',
                source='VIDAL 2026',
            ),
            Interaction(
                medication_a_id=meds[2].id, medication_b_id=meds[1].id,
                severity=InteractionSeverity.CONTRAINDICATED,
                clinical_effect='Risque hémorragique majeur',
                recommendation='CONTRE-INDIQUÉ – ne pas associer',
                source='WHO',
            ),
            Interaction(
                medication_a_id=meds[3].id, medication_b_id=meds[1].id,
                severity=InteractionSeverity.MAJOR,
                clinical_effect='Risque hémorragique accru + insuffisance rénale',
                recommendation='Éviter lassociation, surveiller fonction rénale',
                source='VIDAL',
            ),
            Interaction(
                medication_a_id=meds[7].id, medication_b_id=meds[1].id,
                severity=InteractionSeverity.MODERATE,
                clinical_effect='Risque hémorragique léger',
                recommendation='Surveillance INR si Warfarine au long cours',
                source='Medimefi',
            ),
            Interaction(
                medication_a_id=meds[6].id, medication_b_id=meds[9].id,
                severity=InteractionSeverity.MINOR,
                clinical_effect='Possible diminution absorption simvastatine',
                recommendation='Prendre à distance (2h avant ou après)',
                source='ClinPK',
            ),
        ]
        session.add_all(interactions)
        await session.flush()
        print(f'{len(interactions)} interactions créées')

        from app.models.prescription_models import Prescription, PrescriptionStatus
        from datetime import date
        prescriptions = [
            Prescription(
                patient_ipp='IPP-001', patient_name='Jean Dupont',
                medication_id=meds[0].id, dosage_value=500, dosage_unit='mg',
                frequency='3x/jour',
                start_date=date.today(), status=PrescriptionStatus.ACTIVE,
                prescriber_id=existing.id if existing else 1,
            ),
            Prescription(
                patient_ipp='IPP-002', patient_name='Marie Martin',
                medication_id=meds[4].id, dosage_value=50, dosage_unit='mg',
                frequency='2x/jour',
                start_date=date.today(), status=PrescriptionStatus.ACTIVE,
                prescriber_id=existing.id if existing else 1,
            ),
            Prescription(
                patient_ipp='IPP-001', patient_name='Jean Dupont',
                medication_id=meds[9].id, dosage_value=20, dosage_unit='mg',
                frequency='1x/soir',
                start_date=date.today(), status=PrescriptionStatus.ACTIVE,
                prescriber_id=existing.id if existing else 1,
            ),
        ]
        session.add_all(prescriptions)
        await session.flush()
        print(f'{len(prescriptions)} prescriptions créées')

        from app.models.allergy_models import PatientAllergy, AllergenType, AllergySeverity, ReactionType
        allergies = [
            PatientAllergy(
                patient_ipp='IPP-001', allergen_type=AllergenType.MEDICATION,
                allergen_name='Pénicilline', atc_code='J01C',
                severity=AllergySeverity.SEVERE, reaction_type=ReactionType.ANAPHYLAXIS, confirmed=True,
            ),
            PatientAllergy(
                patient_ipp='IPP-001', allergen_type=AllergenType.MEDICATION,
                allergen_name='Aspirine', atc_code='N02BA',
                severity=AllergySeverity.MODERATE, reaction_type=ReactionType.RASH, confirmed=True,
            ),
        ]
        session.add_all(allergies)
        print(f'{len(allergies)} allergies créées')

        await session.commit()
        print('Seed COMPLET - données de test prêtes!')


if __name__ == '__main__':
    asyncio.run(init())
    uvicorn.run('app.main:app', host='0.0.0.0', port=9600, factory=False)