import asyncio
from redis import asyncio as aioredis  # ✅ Modern way (aioredis is deprecated)
import json
from math import ceil
from config import Config

async def fetch_from_redis(tahun='2026', instansi=None, kategoriId=None, page=1, per_page=100, tahapan=None, status=None, kementerian=None, search_nama=None):
    redis = await aioredis.from_url(Config.REDIS_URL)
    redis_key = f"spse:{tahun}:tender"

    items = await redis.lrange(redis_key, 0, -1)
    await redis.close()

    results = [json.loads(item) for item in items]

    # Filter jika ada parameter
    if instansi:
        results = [r for r in results if r.get("instansi") == instansi]
    if kementerian:
        # Filter berdasarkan Satuan Kerja (index 2)
        results = [r for r in results if r.get("2") == kementerian]
    if kategoriId:
        results = [r for r in results if r.get("8") == kategoriId]
    if tahapan:
        results = [r for r in results if r.get("3") == tahapan]
    if status:
        if status == "Selesai":
            results = [r for r in results if r.get("3") == "Tender Sudah Selesai"]
        elif status == "Aktif":
            results = [r for r in results if r.get("3") != "Tender Sudah Selesai" and "Batal" not in (r.get("3") or "") and "Gagal" not in (r.get("3") or "")]
        elif status == "Batal":
            results = [r for r in results if "Batal" in (r.get("3") or "")]
        elif status == "Gagal":
            results = [r for r in results if "Gagal" in (r.get("3") or "")]
    if search_nama:
        # Case-insensitive search di field nama paket (index '1')
        search_lower = search_nama.lower()
        results = [r for r in results if search_lower in (r.get("1") or "").lower()]

    # Sort by tahapan (field '3') - prioritize active tenders
    def sort_key(item):
        tahapan = item.get("3") or ""
        # Priority order: Active stages first, then completed, then cancelled/failed
        if "Selesai" in tahapan:
            return (2, tahapan)  # Completed tenders - medium priority
        elif "Batal" in tahapan or "Gagal" in tahapan:
            return (3, tahapan)  # Cancelled/failed - lowest priority
        else:
            return (1, tahapan)  # Active tenders - highest priority

    results.sort(key=sort_key)

    # Pagination
    total = len(results)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    paged_results = results[start:end]

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "data": paged_results,
        "tahun": tahun
    }

def fetch(tahun='2026', instansi=None, kategoriId=None, page=1, per_page=100, tahapan=None, status=None, kementerian=None, search_nama=None):
    return asyncio.run(fetch_from_redis(tahun=tahun, instansi=instansi, kategoriId=kategoriId, page=page, per_page=per_page, tahapan=tahapan, status=status, kementerian=kementerian, search_nama=search_nama))
