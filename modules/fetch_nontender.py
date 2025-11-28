import asyncio
from redis import asyncio as aioredis  # ✅ Modern way (aioredis is deprecated)
import json
from math import ceil
from config import Config

async def fetch_from_redis(tahun='2025', instansi=None, kategoriId=None, page=1, per_page=100):
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

def fetch(tahun='2025', instansi=None, kategoriId=None, page=1, per_page=100):
    return asyncio.run(fetch_from_redis(tahun=tahun, instansi=instansi, kategoriId=kategoriId, page=page, per_page=per_page))
