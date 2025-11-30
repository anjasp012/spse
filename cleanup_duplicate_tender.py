"""
Script untuk membersihkan data tender yang duplikat di Redis.
Jalankan script ini untuk menghapus data duplikat berdasarkan kode tender.
"""
import asyncio
from redis import asyncio as aioredis
import json
from config import Config

async def cleanup_duplicates(tahun):
    redis = await aioredis.from_url(Config.REDIS_URL)
    redis_key = f"spse:{tahun}:tender"

    print(f"[INFO] Memeriksa duplikasi untuk tahun {tahun}...")

    # Ambil semua data
    items = await redis.lrange(redis_key, 0, -1)
    print(f"[INFO] Total data: {len(items)}")

    if not items:
        print(f"[WARNING] Tidak ada data untuk tahun {tahun}")
        await redis.close()
        return

    # Track kode yang sudah ditemukan dan data unik
    seen_codes = set()
    unique_data = []
    duplicate_count = 0

    for item in items:
        row_dict = json.loads(item)
        kode_tender = row_dict.get("0")

        if kode_tender:
            if kode_tender not in seen_codes:
                seen_codes.add(kode_tender)
                unique_data.append(item)
            else:
                duplicate_count += 1
        else:
            # Data tanpa kode tetap disimpan
            unique_data.append(item)

    print(f"[INFO] Ditemukan {duplicate_count} data duplikat")
    print(f"[INFO] Data unik: {len(unique_data)}")

    if duplicate_count > 0:
        print(f"[INFO] Membersihkan duplikasi...")

        # Hapus semua data lama
        await redis.delete(redis_key)

        # Simpan ulang data yang unik
        if unique_data:
            await redis.rpush(redis_key, *unique_data)

        print(f"[SUCCESS] Selesai! {duplicate_count} duplikasi telah dihapus")
        print(f"[INFO] Total data sekarang: {len(unique_data)}")
    else:
        print(f"[SUCCESS] Tidak ada duplikasi ditemukan")

    await redis.close()

async def cleanup_all_years():
    """Cleanup untuk semua tahun yang tersedia"""
    years = [2020, 2021, 2022, 2023, 2024, 2025]

    print("=" * 60)
    print("CLEANUP DUPLIKASI DATA TENDER")
    print("=" * 60)

    for year in years:
        await cleanup_duplicates(year)
        print("-" * 60)

    print("\n[SUCCESS] Cleanup selesai untuk semua tahun!")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Cleanup untuk tahun spesifik
        try:
            tahun = int(sys.argv[1])
            asyncio.run(cleanup_duplicates(tahun))
        except ValueError:
            print("[ERROR] Error: Tahun harus berupa angka")
            print("Contoh: python cleanup_duplicate_tender.py 2025")
    else:
        # Cleanup untuk semua tahun
        asyncio.run(cleanup_all_years())
