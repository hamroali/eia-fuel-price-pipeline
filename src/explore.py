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
}

# 4. So'rov yuborish va tekshirish
response = requests.get(url, params=params, timeout=30)
print("Status kodi:", response.status_code)

if response.status_code != 200:
    raise SystemExit(f"Xato: server {response.status_code} qaytardi. Javob: {response.text[:300]}")

# 5. Javobni o'qish
data = response.json()
print("Jami qatorlar:", data["response"]["total"])
print("Birinchi yozuv:", data["response"]["data"][0])

# 6. Bronze qatlamga saqlash                                  # YANGI BO'LIM
BASE_DIR = Path(__file__).resolve().parent.parent
bronze_dir = BASE_DIR / "data" / "bronze" / "spot"
bronze_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
file_path = bronze_dir / f"spot_{timestamp}.json"

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saqlandi:", file_path.relative_to(BASE_DIR))