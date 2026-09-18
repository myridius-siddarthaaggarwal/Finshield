import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.db.session import SessionLocal
from app.models.case import RiskCase

def delete_test_cases():
    db = SessionLocal()
    try:
        # Delete cases with ID in [8, 9, 10, 11, 12, 13]
        target_ids = [8, 9, 10, 11, 12, 13]
        cases_to_delete = db.query(RiskCase).filter(RiskCase.id.in_(target_ids)).all()
        
        deleted_ids = []
        for c in cases_to_delete:
            deleted_ids.append(c.id)
            db.delete(c)
        
        db.commit()
        print(f"Successfully deleted {len(deleted_ids)} duplicate test cases: {deleted_ids}")

        remaining = db.query(RiskCase).order_by(RiskCase.id.asc()).all()
        print("\nCurrent Remaining Cases in FinShield Database:")
        for c in remaining:
            print(f"  • Case #{c.case_number or c.id} (ID: {c.id}): {c.title} [{c.division} | {c.status}]")

    except Exception as e:
        db.rollback()
        print(f"Error during deletion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_test_cases()
