import asyncio
from redis import asyncio as aioredis  # ✅ Modern way (aioredis is deprecated)
import json
from math import ceil
from config import Config

async def fetch_from_redis(tahun='2026', instansi=None, kategoriId=None, page=1, per_page=100, search_nama=None, kementerian=None, tahapan=None):
    redis = await aioredis.from_url(Config.REDIS_URL)
    redis_key = f"spse:{tahun}:nontender"

    items = await redis.lrange(redis_key, 0, -1)
    await redis.close()

    results = [json.loads(item) for item in items]

    # Filter jika ada parameter
    if instansi:
        results = [r for r in results if r.get("instansi") == instansi]
    if kategoriId:
        results = [r for r in results if r.get("6") == kategoriId]
    if search_nama:
        search_nama_lower = search_nama.lower()
        results = [r for r in results if search_nama_lower in str(r.get("1", "")).lower()]
    if kementerian:
        results = [r for r in results if kementerian.lower() in str(r.get("2", "")).lower()]
    if tahapan:
        # Filter dengan mencocokkan 3-4 kata pertama
        tahapan_words = tahapan.split()[:4]  # Ambil max 4 kata pertama dari filter
        results = [r for r in results if all(word in (r.get("3") or "").split()[:4] for word in tahapan_words)]

    # Sort by tahapan (field '3') - prioritize active non-tenders
    def sort_key(item):
        tahapan = item.get("3") or ""
        # Priority order: Active stages first, then completed, then cancelled/failed
        if "Selesai" in tahapan:
            return (2, tahapan)  # Completed - medium priority
        elif "Batal" in tahapan or "Gagal" in tahapan:
            return (3, tahapan)  # Cancelled/failed - lowest priority
        else:
            return (1, tahapan)  # Active - highest priority

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

def fetch(tahun='2026', instansi=None, kategoriId=None, page=1, per_page=100, search_nama=None, kementerian=None, tahapan=None):
    return asyncio.run(fetch_from_redis(tahun=tahun, instansi=instansi, kategoriId=kategoriId, page=page, per_page=per_page, search_nama=search_nama, kementerian=kementerian, tahapan=tahapan))
