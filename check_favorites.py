"""
Check for duplicate favorites or issues
"""
from app import app, db
from models import Favorite, User
from sqlalchemy import func

def check_favorites():
    with app.app_context():
        print("=== FAVORITE DATABASE CHECK ===\n")

        # Get all favorites
        all_favs = Favorite.query.all()
        print(f"Total favorites: {len(all_favs)}\n")

        # Group by user
        print("Favorites by user:")
        users = User.query.all()
        for user in users:
            tender_favs = Favorite.query.filter_by(user_id=user.id, type='tender').all()
            nontender_favs = Favorite.query.filter_by(user_id=user.id, type='nontender').all()

            print(f"\nUser: {user.username} (ID: {user.id})")
            print(f"  Tender favorites ({len(tender_favs)}):")
            for fav in tender_favs:
                print(f"    - {fav.kode_tender}")

            print(f"  Non-Tender favorites ({len(nontender_favs)}):")
            for fav in nontender_favs:
                print(f"    - {fav.kode_tender}")

        # Check for potential duplicates (same kode, same user, different type)
        print("\n=== Checking for same kode across types ===")
        duplicates = db.session.query(
            Favorite.user_id,
            Favorite.kode_tender,
            func.count(Favorite.id).label('count')
        ).group_by(Favorite.user_id, Favorite.kode_tender).having(func.count(Favorite.id) > 1).all()

        if duplicates:
            print(f"Found {len(duplicates)} kode that exist in multiple types:")
            for user_id, kode, count in duplicates:
                user = User.query.get(user_id)
                favs = Favorite.query.filter_by(user_id=user_id, kode_tender=kode).all()
                print(f"  User {user.username} has kode '{kode}' favorited {count} times:")
                for fav in favs:
                    print(f"    - type: {fav.type}")
        else:
            print("No duplicates found (same kode on different types is OK)")

if __name__ == '__main__':
    check_favorites()
