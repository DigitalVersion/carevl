#!/usr/bin/env python3
"""
Migration script from Phase 1 to Phase 2 schema
Migrate flat JSON records to FHIR-aligned relational structure
"""

import sys
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import (
    Patient, PatientIdentifier, Encounter, EncounterParticipant,
    Observation, Condition, Questionnaire, QuestionnaireResponse,
    AuditEvent
)


def generate_uuid():
    """Generate UUID v4"""
    return str(uuid.uuid4())


def migrate_patient(session, record_data, station_id):
    """
    Migrate patient data from flat JSON to Patient + PatientIdentifiers
    Returns patient_id
    """
    # Extract demographics
    full_name = record_data.get("full_name", "")
    birth_date = record_data.get("birth_date")
    gender = record_data.get("gender", "unknown")
    phone = record_data.get("phone_number")
    
    # Generate patient UUID
    patient_id = generate_uuid()
    
    # Create Patient
    patient = Patient(
        id=patient_id,
        full_name=full_name,
        birth_date=birth_date,
        gender_code=gender,
        phone_number=phone,
        station_id=station_id,
        raw_json=json.dumps(record_data)
    )
    session.add(patient)
    
    # Create PatientIdentifiers
    cccd = record_data.get("cccd")
    if cccd:
        identifier = PatientIdentifier(
            patient_id=patient_id,
            system="CCCD",
            value=cccd
        )
        session.add(identifier)
    
    bhyt = record_data.get("bhyt")
    if bhyt:
        identifier = PatientIdentifier(
            patient_id=patient_id,
            system="BHYT",
            value=bhyt
        )
        session.add(identifier)
    
    return patient_id


def migrate_encounter(session, record, patient_id, station_id):
    """
    Migrate encounter from old record to Encounter
    Returns encounter_id
    """
    encounter_id = record.get("id") or generate_uuid()
    
    encounter = Encounter(
        id=encounter_id,
        patient_id=patient_id,
        sticker_id=record.get("sticker_id"),
        encounter_date=record.get("encounter_date") or datetime.now(timezone.utc),
        package_id=record.get("package_id"),
        station_id=station_id,
        commune_code=record.get("commune_code"),
        author=record.get("author"),
        summary_text=record.get("summary_text"),
        classification_display=record.get("classification_display"),
        sync_state="pending",
        raw_json=json.dumps(record)
    )
    session.add(encounter)
    
    # Add author as participant
    if record.get("author"):
        participant = EncounterParticipant(
            encounter_id=encounter_id,
            participant_type="data_entry",
            participant_name=record["author"]
        )
        session.add(participant)
    
    return encounter_id


def migrate_observations(session, record_data, encounter_id, patient_id, station_id):
    """
    Extract observations from dynamic form data
    """
    # Example: extract vital signs
    vital_signs = record_data.get("vital_signs", {})
    
    for code, value in vital_signs.items():
        if value:
            obs = Observation(
                id=generate_uuid(),
                encounter_id=encounter_id,
                patient_id=patient_id,
                code_system="local",
                code=code,
                code_display=code.replace("_", " ").title(),
                category="vital-signs",
                value_type="numeric" if isinstance(value, (int, float)) else "string",
                value_numeric=value if isinstance(value, (int, float)) else None,
                value_string=str(value) if not isinstance(value, (int, float)) else None,
                station_id=station_id,
                effective_datetime=datetime.now(timezone.utc)
            )
            session.add(obs)


def migrate_conditions(session, record_data, encounter_id, patient_id, station_id):
    """
    Extract conditions from diagnosis/history fields
    """
    diagnosis = record_data.get("diagnosis")
    if diagnosis:
        condition = Condition(
            id=generate_uuid(),
            patient_id=patient_id,
            encounter_id=encounter_id,
            code_system="local",
            code="diagnosis",
            code_display=diagnosis,
            category="encounter-diagnosis",
            clinical_status="active",
            verification_status="confirmed",
            station_id=station_id
        )
        session.add(condition)


def migrate_questionnaire_response(session, record_data, questionnaire_id, encounter_id, patient_id, station_id, author):
    """
    Store full form response as QuestionnaireResponse
    """
    response = QuestionnaireResponse(
        id=generate_uuid(),
        questionnaire_id=questionnaire_id,
        encounter_id=encounter_id,
        patient_id=patient_id,
        status="completed",
        response_json=json.dumps(record_data),
        author=author,
        station_id=station_id
    )
    session.add(response)


def create_audit_event(session, event_type, resource_type, resource_id, station_id, description):
    """
    Create audit event for tracking
    """
    audit = AuditEvent(
        event_type=event_type,
        event_outcome="success",
        resource_type=resource_type,
        resource_id=resource_id,
        agent_type="system",
        agent_name="migration_script",
        source_station_id=station_id,
        description=description
    )
    session.add(audit)


def migrate_database(db_path: str, station_id: str):
    """
    Main migration function
    """
    print(f"Starting migration for database: {db_path}")
    print(f"Station ID: {station_id}")
    
    # Connect to database
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create default questionnaire if not exists
        questionnaire_id = "q-default-v1"
        existing_q = session.query(Questionnaire).filter_by(id=questionnaire_id).first()
        if not existing_q:
            questionnaire = Questionnaire(
                id=questionnaire_id,
                title="Default Health Screening Form",
                version="1.0.0",
                status="active",
                definition_json='{"sections": []}',
                station_id=station_id
            )
            session.add(questionnaire)
            session.commit()
            print(f"Created default questionnaire: {questionnaire_id}")
        
        # Query old records (assuming they exist in a 'records' table)
        # Adjust this based on your actual Phase 1 schema
        result = session.execute(text("SELECT * FROM records WHERE synced = 0"))
        records = result.fetchall()
        
        print(f"Found {len(records)} records to migrate")
        
        migrated_count = 0
        for record in records:
            try:
                # Parse record data
                record_dict = dict(record._mapping)
                record_data = json.loads(record_dict.get("data", "{}"))
                
                # Step 1: Migrate patient
                patient_id = migrate_patient(session, record_data, station_id)
                
                # Step 2: Migrate encounter
                encounter_id = migrate_encounter(session, record_dict, patient_id, station_id)
                
                # Step 3: Migrate observations
                migrate_observations(session, record_data, encounter_id, patient_id, station_id)
                
                # Step 4: Migrate conditions
                migrate_conditions(session, record_data, encounter_id, patient_id, station_id)
                
                # Step 5: Migrate questionnaire response
                migrate_questionnaire_response(
                    session, record_data, questionnaire_id, 
                    encounter_id, patient_id, station_id,
                    record_dict.get("author")
                )
                
                # Step 6: Create audit event
                create_audit_event(
                    session, "migrate", "encounter", encounter_id,
                    station_id, f"Migrated from Phase 1 record {record_dict.get('id')}"
                )
                
                migrated_count += 1
                
                if migrated_count % 10 == 0:
                    session.commit()
                    print(f"Migrated {migrated_count} records...")
                
            except Exception as e:
                print(f"Error migrating record {record_dict.get('id')}: {e}")
                session.rollback()
                continue
        
        # Final commit
        session.commit()
        print(f"\nMigration completed successfully!")
        print(f"Total records migrated: {migrated_count}")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python migrate_to_phase2.py <db_path> <station_id>")
        print("Example: python migrate_to_phase2.py data/carevl.db station-001")
        sys.exit(1)
    
    db_path = sys.argv[1]
    station_id = sys.argv[2]
    
    migrate_database(db_path, station_id)
