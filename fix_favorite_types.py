"""
Fix existing favorites that have NULL or missing type field
Set all existing favorites to 'tender' by default
"""
from app import app, db
from models import Favorite

def fix_existing_favorites():
    with app.app_context():
        try:
            # Update all favorites with NULL type to 'tender'
            updated = db.session.query(Favorite).filter(Favorite.type == None).update({Favorite.type: 'tender'})

            # Also update empty strings if any
            updated2 = db.session.query(Favorite).filter(Favorite.type == '').update({Favorite.type: 'tender'})

            db.session.commit()

            total = updated + updated2
            print(f"[SUCCESS] Updated {total} favorites to have type='tender'")

            # Show stats
            tender_count = Favorite.query.filter_by(type='tender').count()
            nontender_count = Favorite.query.filter_by(type='nontender').count()

            print(f"Current stats:")
            print(f"  - Tender favorites: {tender_count}")
            print(f"  - Non-tender favorites: {nontender_count}")

        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Failed to update: {e}")
            raise

if __name__ == '__main__':
    fix_existing_favorites()
