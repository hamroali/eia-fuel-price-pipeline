"""Chakana dizel narxlari uchun qaysi seriyalar mavjudligini aniqlash."""
import requests
from extract import get_api_key

api_key = get_api_key()

params = {
    "api_key": api_key,
    "frequency": "weekly",
    "data[0]": "value",
    "facets[product][]": "EPD2DXL0",
    "start": "2026-09-01",
}
response = requests.get("https://api.eia.gov/v2/petroleum/pri/gnd/data/", params=params, timeout=30)
records = response.json()["response"]["data"]

seen = set()
for r in records:
    key = (r["series"], r["duoarea"], r["area-name"])
    if key not in seen:
        seen.add(key)
        print(key)