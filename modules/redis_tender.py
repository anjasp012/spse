import asyncio
import aiohttp
import re
import random
from redis import asyncio as aioredis  # ✅ Modern way (aioredis is deprecated)
import json
from config import Config

instances = [
    "pertanian",
    "jakarta",
    "babelprov",
    "katingankab",
    "malakakab",
    "usu",
    "ui",
    "undip",
    "lkpp",
    "kemenkeu",
    "sumutprov",
    "sumselprov",
    "sumbarprov",
    "sulutprov",
    "sultraprov",
    "sultengprov",
    "sulselprov",
    "sulbarprov",
    "riau",
    "nasional",
    "bin",
    "bnpp",
    "karantinaindonesia",
    "ndugakab",
    "paniaikab",
    "polkam",
    "wantannas",
    "badanpangan",
    "kotamobagu",
    "acehprov",
    "kemenkeu",
    "big",
    "bakamla",
    "bkn",
    "kemendukbangga",
    "bmkg",
    "bnn",
    "bnpb",
    "bnpt",
    "basarnas",
    "kemenkeu",
    "pom",
    "bpkp",
    "bpbatam",
    "bpbatam",
    "kemenkeu",
    "kp2mi",
    "bps",
    "brin",
    "bssn",
    "brin",
    "kemenkeu",
    "lkpp",
    "papua",
    "dpd",
    "dpr",
    "acehbaratkab",
    "acehbaratdayakab",
    "acehbesarkab",
    "acehjayakab",
    "acehselatankab",
    "acehsingkilkab",
    "acehtamiangkab",
    "acehtengahkab",
    "acehtenggarakab",
    "acehtimurkab",
    "acehutara",
    "agamkab",
    "alorkab",
    "asahankab",
    "asmatkab",
    "badungkab",
    "bandungbaratkab",
    "banggaikab",
    "banggaikep",
    "banggailautkab",
    "bangka",
    "bangkabaratkab",
    "bangkaselatankab",
    "bangkatengahkab",
    "bangkalankab",
    "banglikab",
    "banjarkab",
    "banjarnegarakab",
    "bantaengkab",
    "bantulkab",
    "banyuasinkab",
    "banyumaskab",
    "banyuwangikab",
    "baritokualakab",
    "baritoselatankab",
    "baritotimurkab",
    "baritoutarakab",
    "barrukab",
    "batangkab",
    "batangharikab",
    "batubarakab",
    "bekasikab",
    "belitung",
    "beltim",
    "belukab",
    "benermeriahkab",
    "bengkaliskab",
    "bengkayangkab",
    "bengkuluselatankab",
    "bengkulutengahkab",
    "bengkuluutarakab",
    "beraukab",
    "biakkab",
    "bimakab",
    "bintankab",
    "bireuenkab",
    "blitarkab",
    "blorakab",
    "boalemokab",
    "bogorkab",
    "bojonegorokab",
    "bolmongkab",
    "bolselkab",
    "boltimkab",
    "bolmutkab",
    "bombanakab",
    "bondowosokab",
    "bone",
    "bonebolangokab",
    "bovendigoelkab",
    "boyolali",
    "brebeskab",
    "bulelengkab",
    "bulukumbakab",
    "bulungan",
    "bungokab",
    "buolkab",
    "burukab",
    "burselkab",
    "butonkab",
    "butonselatankab",
    "butontengahkab",
    "butonutarakab",
    "ciamiskab",
    "cianjurkab",
    "cilacapkab",
    "cirebonkab",
    "dairikab",
    "deiyaikab",
    "deliserdangkab",
    "demakkab",
    "dharmasrayakab",
    "dogiyaikab",
    "dompukab",
    "donggala",
    "empatlawangkab",
    "endekab",
    "enrekangkab",
    "fakfakkab",
    "florestimurkab",
    "jabarprov",
    "gayolueskab",
    "gianyarkab",
    "gorontalokab",
    "gorutkab",
    "gowakab",
    "gresikkab",
    "grobogan",
    "gunungmaskab",
    "gunungkidulkab",
    "halbarkab",
    "halmaheraselatankab",
    "haltengkab",
    "haltimkab",
    "halmaherautarakab",
    "hulusungaiselatankab",
    "hstkab",
    "hsu",
    "humbanghasundutankab",
    "inhilkab",
    "inhukab",
    "indramayukab",
    "intanjayakab",
    "jayapurakab",
    "jayawijayakab",
    "jemberkab",
    "jembranakab",
    "jenepontokab",
    "jepara",
    "jombangkab",
    "kaimanakab",
    "kamparkab",
    "kapuaskab",
    "kapuashulukab",
    "karanganyarkab",
    "karangasemkab",
    "karawangkab",
    "karimunkab",
    "karokab",
    "kaurkab",
    "kayongutarakab",
    "kebumenkab",
    "kedirikab",
    "keeromkab",
    "kendalkab",
    "sitarokab",
    "kepahiangkab",
    "anambaskab",
    "kepulauanarukab",
    "mentawaikab",
    "merantikab",
    "sangihekab",
    "kepulauanselayarkab",
    "kepulauansulakab",
    "talaudkab",
    "tanimbar",
    "kepyapenkab",
    "kerincikab",
    "ketapangkab",
    "klaten",
    "klungkungkab",
    "kolakakab",
    "kolakatimurkab",
    "kolutkab",
    "konawekab",
    "konkepkab",
    "konaweselatankab",
    "konaweutarakab",
    "kotabarukab",
    "kotawaringinbaratkab",
    "kotimkab",
    "kuansing",
    "kuburayakab",
    "kuduskab",
    "kulonprogokab",
    "kuningankab",
    "kupangkab",
    "kutaibaratkab",
    "kukarkab",
    "kutaitimurkab",
    "labuhanbatukab",
    "labuhanbatuselatankab",
    "labura",
    "lahatkab",
    "lamandaukab",
    "lamongankab",
    "lampungbaratkab",
    "lampungtengahkab",
    "lampungutarakab",
    "landakkab",
    "langkatkab",
    "lannyjayakab",
    "lebakkab",
    "lebongkab",
    "lembatakab",
    "limapuluhkotakab",
    "linggakab",
    "lombokbaratkab",
    "lomboktengahkab",
    "lomboktimurkab",
    "lombokutarakab",
    "lumajangkab",
    "luwukab",
    "luwutimurkab",
    "luwuutarakab",
    "madiunkab",
    "magelangkab",
    "magetan",
    "mahakamulukab",
    "majalengkakab",
    "majenekab",
    "malangkab",
    "malinau",
    "malukubaratdayakab",
    "maltengkab",
    "malukutenggarakab",
    "mamasakab",
    "mamberamorayakab",
    "mamberamotengahkab",
    "mamujukab",
    "mamujutengahkab",
    "madina",
    "manggaraikab",
    "manggaraibaratkab",
    "manggaraitimurkab",
    "manokwarikab",
    "manselkab",
    "mappikab",
    "maroskab",
    "malakakab",
    "melawikab",
    "mempawahkab",
    "meranginkab",
    "merauke",
    "mesujikab",
    "mimikakab",
    "minahasa",
    "minselkab",
    "mitrakab",
    "minut",
    "mojokertokab",
    "morowalikab",
    "morowaliutarakab",
    "muaraenimkab",
    "muarojambikab",
    "mukomukokab",
    "munakab",
    "munabaratkab",
    "murungrayakab",
    "mubakab",
    "musirawaskab",
    "muratarakab",
    "malakakab",
    "nabirekab",
    "naganrayakab",
    "nagekeokab",
    "natunakab",
    "ngadakab",
    "nganjukkab",
    "ngawikab",
    "niaskab",
    "niasbaratkab",
    "niasselatankab",
    "niasutarakab",
    "nunukankab",
    "oganilirkab",
    "kaboki",
    "okukab",
    "okuselatankab",
    "okutimurkab",
    "pacitankab",
    "padanglawaskab",
    "padanglawasutarakab",
    "padangpariamankab",
    "pakpakbharatkab",
    "pamekasankab",
    "pandeglangkab",
    "jabarprov",
    "pangkepkab",
    "parigimoutongkab",
    "pasamankab",
    "pasamanbaratkab",
    "pasangkayukab",
    "paserkab",
    "pasuruankab",
    "patikab",
    "pegafkab",
    "pegbintangkab",
    "pekalongankab",
    "pelalawankab",
    "pemalangkab",
    "penajamkab",
    "palikab",
    "pesawarankab",
    "pesisirbaratkab",
    "pesisirselatankab",
    "pidiekab",
    "pidiejayakab",
    "acehprov",
    "pinrangkab",
    "pohuwatokab",
    "polmankab",
    "ponorogo",
    "posokab",
    "pringsewukab",
    "probolinggokab",
    "pulangpisaukab",
    "pulaumorotaikab",
    "taliabukab",
    "puncakkab",
    "puncakjayakab",
    "purbalinggakab",
    "purwakartakab",
    "purworejokab",
    "rajaampatkab",
    "rejanglebongkab",
    "rembangkab",
    "rohilkab",
    "rokanhulukab",
    "rotendaokab",
    "saburaijuakab",
    "sambas",
    "samosirkab",
    "sampangkab",
    "sanggau",
    "sarmikab",
    "sarolangunkab",
    "sekadaukab",
    "selumakab",
    "semarangkab",
    "sbbkab",
    "serambagiantimurkab",
    "serangkab",
    "serdangbedagaikab",
    "seruyankab",
    "siakkab",
    "sidrapkab",
    "sidoarjokab",
    "sigikab",
    "sijunjung",
    "sikkakab",
    "simalungunkab",
    "simeuluekab",
    "sinjaikab",
    "sintang",
    "situbondokab",
    "slemankab",
    "solokkab",
    "solselkab",
    "soppeng",
    "sorongkab",
    "sorongselatankab",
    "sragenkab",
    "subang",
    "sukabumikab",
    "sukamarakab",
    "sukoharjokab",
    "sumbabaratkab",
    "sbdkab",
    "sumbatengahkab",
    "sumbatimurkab",
    "sumbawakab",
    "sumbawabaratkab",
    "sumedangkab",
    "sumenepkab",
    "supiorikab",
    "tabalongkab",
    "tabanankab",
    "takalarkab",
    "tambrauwkab",
    "tanatidungkab",
    "tanatorajakab",
    "tanahbumbukab",
    "tanahdatar",
    "tanahlautkab",
    "tangerangkab",
    "tanggamus",
    "tanjabbarkab",
    "tanjabtimkab",
    "tapselkab",
    "tapteng",
    "taputkab",
    "tapinkab",
    "tasikmalayakab",
    "tebokab",
    "tegalkab",
    "telukbintunikab",
    "wondamakab",
    "temanggungkab",
    "ttskab",
    "ttukab",
    "tobakab",
    "tojounauna",
    "tolitolikab",
    "tolikarakab",
    "torajautarakab",
    "trenggalekkab",
    "tubankab",
    "tubaba",
    "tulungagung",
]

async def scrape_instance(session, redis, slug, tahun, retries=3):
    base = f"https://spse.inaproc.id/{slug}/lelang"

    for attempt in range(1, retries + 1):
        try:
            # Delay random untuk menghindari rate limiting
            await asyncio.sleep(random.uniform(0.5, 1.5))

            async with session.get(base) as resp:
                if resp.status == 429:
                    raise Exception(f"429 Too Many Requests - Rate limited")
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
            data_url = f"https://spse.inaproc.id/{slug}/dt/lelang?tahun={tahun}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://spse.inaproc.id",
                "Referer": "https://spse.inaproc.id/",
                "Cookie": cookie_string
            }
            post_data = {
                "draw": 1,
                "start": 0,
                "length": 1000000,
                "authenticityToken": token
            }

            async with session.post(data_url, headers=headers, data=post_data) as resp:
                if resp.status == 429:
                    raise Exception(f"429 Too Many Requests pada POST - Rate limited")
                if resp.status != 200:
                    raise Exception(f"POST data gagal, status: {resp.status}")

                json_data = await resp.json()
                redis_key = f"spse:{tahun}:tender"
                redis_set_key = f"spse:{tahun}:tender:codes"  # Set untuk tracking kode yang sudah ada

                # Loop dan simpan data dengan pengecekan duplikasi
                for row in json_data.get("data", []):
                    row_dict = {str(i): v for i,v in enumerate(row)}
                    row_dict["instansi"] = slug

                    # Kode tender ada di index 0
                    kode_tender = row_dict.get("0")
                    if kode_tender:
                        # Cek apakah kode sudah ada di set
                        is_duplicate = await redis.sismember(redis_set_key, kode_tender)
                        if not is_duplicate:
                            # Simpan data dan tambahkan kode ke set
                            await redis.rpush(redis_key, json.dumps(row_dict))
                            await redis.sadd(redis_set_key, kode_tender)

                return True

        except Exception as e:
            if attempt < retries:
                # Exponential backoff: tunggu lebih lama tiap retry
                wait_time = random.uniform(3.0, 8.0) * attempt
                print(f"⚠ Retry {attempt}/{retries} untuk {slug}: {e} (tunggu {wait_time:.1f}s)")
                await asyncio.sleep(wait_time)
            else:
                print(f"Gagal scrape {slug}: {e}")
                return False

async def fetch_and_store(tahun):
    redis = await aioredis.from_url(Config.REDIS_URL)
    redis_key = f"spse:{tahun}:tender"
    redis_set_key = f"spse:{tahun}:tender:codes"

    # Hapus key lama di awal (both list and set)
    deleted_count = 0
    if await redis.exists(redis_key):
        await redis.delete(redis_key)
        deleted_count += 1
    if await redis.exists(redis_set_key):
        await redis.delete(redis_set_key)
        deleted_count += 1

    if deleted_count > 0:
        print(f"🗑 Menghapus data lama untuk tahun {tahun}")

    async with aiohttp.ClientSession() as session:
        remaining = instances.copy()
        total = len(remaining)
        attempt_num = 1

        while remaining:
            print(f"\n📊 Attempt #{attempt_num}: Scraping {len(remaining)} instances dari total {total}")

            # PENTING: Batasi concurrent requests untuk menghindari 429
            batch_size = 5  # Hanya 5 request sekaligus (sangat konservatif)
            batches = [remaining[i:i + batch_size] for i in range(0, len(remaining), batch_size)]

            all_results = []
            for batch_idx, batch in enumerate(batches, 1):
                print(f"  ⏳ Batch {batch_idx}/{len(batches)}: Processing {len(batch)} instances...")
                tasks = [scrape_instance(session, redis, slug, tahun) for slug in batch]
                results = await asyncio.gather(*tasks)
                all_results.extend(zip(batch, results))

                # Delay antar batch (PENTING untuk menghindari 429)
                if batch_idx < len(batches):
                    delay = random.uniform(2.0, 4.0)
                    print(f"    💤 Delay {delay:.1f}s sebelum batch berikutnya...")
                    await asyncio.sleep(delay)

            # Filter instance yang gagal
            failed = [slug for slug, success in all_results if not success]

            if failed:
                print(f"\n⚠ {len(failed)} instances gagal, akan diulang setelah delay 10 detik...")
                await asyncio.sleep(10)  # Delay lebih lama sebelum retry semua yang gagal
                attempt_num += 1
            remaining = failed

    # Cleanup duplikasi setelah scraping selesai
    print(f"\n🧹 Membersihkan duplikasi data...")
    await cleanup_duplicates(redis, tahun)

    await redis.close()
    print(f"\n✅ Selesai! Total {total} instances berhasil di-scrape untuk tahun {tahun}")
    return True

async def cleanup_duplicates(redis, tahun):
    """Membersihkan data duplikat berdasarkan kode tender"""
    redis_key = f"spse:{tahun}:tender"

    # Ambil semua data
    items = await redis.lrange(redis_key, 0, -1)

    if not items:
        print(f"   Tidak ada data untuk dibersihkan")
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

    if duplicate_count > 0:
        print(f"   Ditemukan {duplicate_count} duplikasi dari {len(items)} data")

        # Hapus semua data lama
        await redis.delete(redis_key)

        # Simpan ulang data yang unik
        if unique_data:
            await redis.rpush(redis_key, *unique_data)

        print(f"   ✅ {duplicate_count} duplikasi telah dihapus, tersisa {len(unique_data)} data unik")
    else:
        print(f"   ✅ Tidak ada duplikasi ditemukan ({len(unique_data)} data unik)")


def fetch(tahun):
    return asyncio.run(fetch_and_store(tahun))
