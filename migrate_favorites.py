"""
Migration script to remove instansi and nama_paket columns from favorites table
"""
from app import app, db
from models import Favorite

def migrate():
    with app.app_context():
        try:
            # Drop the old columns if they exist
            with db.engine.connect() as conn:
                # Check if columns exist before dropping
                result = conn.execute(db.text("PRAGMA table_info(favorites)"))
                columns = [row[1] for row in result]

                if 'instansi' in columns or 'nama_paket' in columns:
                    print("Migrasi diperlukan. Membuat tabel baru...")

                    # Create backup
                    conn.execute(db.text("""
                        CREATE TABLE IF NOT EXISTS favorites_backup AS
                        SELECT * FROM favorites
                    """))
                    conn.commit()
                    print("✓ Backup tabel favorites dibuat")

                    # Drop old table
                    conn.execute(db.text("DROP TABLE favorites"))
                    conn.commit()
                    print("✓ Tabel favorites lama dihapus")

                    # Create new table with updated schema
                    db.create_all()
                    print("✓ Tabel favorites baru dibuat")

                    # Migrate data (only kode_tender and user_id)
                    conn.execute(db.text("""
                        INSERT INTO favorites (user_id, kode_tender, created_at)
                        SELECT user_id, kode_tender, created_at
                        FROM favorites_backup
                    """))
                    conn.commit()
                    print("✓ Data dimigrasikan")

                    print("\n✅ Migrasi selesai!")
                    print("💡 Tabel backup tersimpan di 'favorites_backup'")
                else:
                    print("✓ Sudah menggunakan schema terbaru, tidak perlu migrasi")

        except Exception as e:
            print(f"❌ Error saat migrasi: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    migrate()
