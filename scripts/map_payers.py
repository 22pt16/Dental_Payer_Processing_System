# scripts/map_payers.py
import os
import sys
from fuzzywuzzy import fuzz


# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app import app
from backend.models import db, PayerDetail, Payer


def get_similarity_score(name1, name2):
    return fuzz.ratio(name1.lower(), name2.lower())

def commit_session(rows_processed):
    """Commit session with rollback on failure."""
    try:
        db.session.commit()
        print(f"Committed {rows_processed} rows")
    except Exception as e:
        print(f"Error committing at {rows_processed}: {e}")
        db.session.rollback()
        raise

def map_payers():
    with app.app_context():
        print("Starting payer mapping...")
        details = db.session.query(PayerDetail).all()
        
        payer_groups = {}
        unmapped = []
        
        # Step 1: Group by payer_id and name similarity
        for detail in details:
            matched = False
            for key in payer_groups:
                canonical_id, canonical_name = key
                name_score = get_similarity_score(detail.payer_name, canonical_name)
                
                # Match if payer_id matches OR name > 85% and state aligns
                if (detail.payer_id == canonical_id) or \
                   (name_score > 85 and (detail.state or None) == payer_groups[key][0].state):
                    payer_groups[key].append(detail)
                    matched = True
                    break
                elif name_score > 70 and name_score <= 85:
                    # Flag for manual review
                    unmapped.append(detail)
                    matched = True
                    break
            
            if not matched:
                payer_groups[(detail.payer_id, detail.payer_name)] = [detail]
        
        # Step 2: Update tables
        rows_processed = 0
        for (payer_id, canonical_name), group in payer_groups.items():
            payer = db.session.query(Payer).filter_by(payer_id=payer_id).first()
            if not payer:
                payer = Payer(
                    payer_id=payer_id,
                    payer_name=canonical_name,
                    pretty_name=canonical_name,
                    group_id="UNKNOWN"
                )
                db.session.add(payer)
            
            for detail in group:
                detail.payer_id = payer_id
                rows_processed += 1
                if rows_processed % 100 == 0:
                    commit_session(rows_processed)
        
        # Step 3: Log unmapped rows
        if unmapped:
            print(f"Flagged {len(unmapped)} rows for manual review:")
            for detail in unmapped[:5]:
                print(f" - {detail.payer_name}, {detail.payer_id}, {detail.source}")
        
        commit_session(rows_processed)
        print(f"Total rows mapped: {rows_processed}")
        print("Mapping complete!")

if __name__ == "__main__":
    map_payers()