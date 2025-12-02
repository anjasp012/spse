"""
Migration script to add 'type' column to favorites table
Run this script to update existing database
"""
from app import app, db
from models import Favorite
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Check if column exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('favorites')]

            if 'type' not in columns:
                print("Adding 'type' column to favorites table...")

                # Add column with default value
                db.session.execute(text("ALTER TABLE favorites ADD COLUMN type VARCHAR(20) DEFAULT 'tender' NOT NULL"))

                # Drop old unique constraint
                try:
                    db.session.execute(text('ALTER TABLE favorites DROP CONSTRAINT unique_user_favorite'))
                    print("Dropped old unique constraint")
                except Exception as e:
                    print(f"Note: {e}")

                # Add new unique constraint
                db.session.execute(text('ALTER TABLE favorites ADD CONSTRAINT unique_user_favorite_type UNIQUE (user_id, kode_tender, type)'))

                db.session.commit()
                print("[SUCCESS] Migration completed successfully!")
            else:
                print("Column 'type' already exists. No migration needed.")

        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Migration failed: {e}")
            raise

if __name__ == '__main__':
    migrate()
