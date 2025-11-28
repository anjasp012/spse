import asyncio
import aiohttp
import re
import json
import time
import random
import logging
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

instances = [
    "pertanian","jakarta","babelprov","katingankab","malakakab","usu",
    "ui","undip","lkpp","kemenkeu","sumutprov","sumselprov",
    "sumbarprov","sulutprov","sultraprov","sultengprov",
    "sulselprov","sulbarprov","riau",
]

async def scrape_instance(session, slug, jenis='', tahun='2025', status='', retries=3):
    base = f"{Config.SPSE_BASE_URL}/{slug}/nontender"

    for attempt in range(1, retries + 1):
        try:
            async with session.get(base) as resp:
                if resp.status != 200:
                    raise Exception(f"GET halaman gagal, status: {resp.status}")

                text = await resp.text()
                cookies = resp.cookies
                cookie_string = "; ".join(f"{k}={v.value}" for k,v in cookies.items())

                match = re.search(r"d\.authenticityToken\s*=\s*'([a-zA-Z0-9]+)'", text)
                token = match.group(1) if match else None
                if not token:
                    raise Exception("Token tidak ditemukan")

            # POST data
            data_url = f"{Config.SPSE_BASE_URL}/{slug}/dt/pl?kategoriId={jenis}&tahun={tahun}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": Config.SPSE_BASE_URL,
                "Referer": f"{Config.SPSE_BASE_URL}/",
                "Cookie": cookie_string
            }
            post_data = {
                "draw": 1,
                "start": 0,
                "length": 1000000,
                "authenticityToken": token
            }

            async with session.post(data_url, headers=headers, data=post_data) as resp:
                if resp.status != 200:
                    raise Exception(f"POST data gagal, status: {resp.status}")

                try:
                    json_data = await resp.json()
                except Exception:
                    raise Exception(f"Response bukan JSON: {await resp.text()}")

                results = []
                for row in json_data.get("data", []):
                    row_dict = {str(i): v for i,v in enumerate(row)}
                    row_dict["instansi"] = slug
                    results.append(row_dict)

                logger.info(f"{slug} selesai, {len(results)} data")
                return results

        except Exception as e:
            logger.warning(f"Gagal scrape {slug} (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                await asyncio.sleep(random.uniform(0.5, 1.5))  # delay sebelum retry
            else:
                logger.error(f"{slug} gagal setelah {retries} percobaan, dilewati.")
                return []

async def main():
    start_time = time.time()
    all_data = []

    async with aiohttp.ClientSession() as session:
        tasks = [scrape_instance(session, slug) for slug in instances]
        results = await asyncio.gather(*tasks)

        for res in results:
            all_data.extend(res)

    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"Scraping selesai dalam {duration:.2f} detik, total {len(all_data)} data")

    with open("spse_all_data_retry.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
