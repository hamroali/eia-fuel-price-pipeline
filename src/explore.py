# 1. Importlar
import os
import json                          # YANGI
from datetime import datetime        # YANGI
from pathlib import Path             # YANGI
import requests
from dotenv import load_dotenv

# 2. Kalitni yuklash va tekshirish
load_dotenv()
api_key = os.getenv("EIA_API_KEY")

if not api_key:
    raise SystemExit("Xato: .env faylida EIA_API_KEY topilmadi")

# 3. So'rov manzili va parametrlari
url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
params = {
    "api_key": api_key,
    "frequency": "daily",
    "data[0]": "value",
    "facets[series][]": "RWTC",
    "start": "2026-09-01",
    "sort[0][column]": "period",
    "sort[0][direction]": "asc",
    "facets[series][]": [
        "RWTC",
        "RBRTE",
        "EER_EPD2DXL0_PF4_Y35NY_DPG",
        "EER_EPD2DXL0_PF4_RGC_DPG",
    ],
    "start": "2024-01-01",
}

# 4. So'rov yuborish (sahifalab)
PAGE_SIZE = 5000
all_records = []
pages = []
offset = 0

while True:
    params["offset"] = offset
    params["length"] = PAGE_SIZE

    response = requests.get(url, params=params, timeout=30)
    if response.status_code != 200:
        raise SystemExit(f"Xato: server {response.status_code} qaytardi. Javob: {response.text[:300]}")

    data = response.json()
    page = data["response"]["data"]
    total = int(data["response"]["total"])

    pages.append(data)
    all_records.extend(page)
    print(f"Sahifa: offset={offset}, keldi={len(page)}, jami={total}")

    offset += len(page)
    if not page or offset >= total:
        break

# 5. Natijani tekshirish
print("Qabul qilindi:", len(all_records), "/", total)
print("Birinchi yozuv:", all_records[0])