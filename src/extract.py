"""Extract: EIA API'dan ma'lumot olish va Bronze qatlamga saqlash."""

# Importlar
import os
import json
from datetime import datetime
from pathlib import Path
import logging
import requests
from dotenv import load_dotenv


# Sozlamalar
BASE_DIR = Path(__file__).resolve().parent.parent
log = logging.getLogger(__name__)
API_BASE_URL = "https://api.eia.gov/v2"
PAGE_SIZE = 5000
TIMEOUT = 30


def get_api_key():
    load_dotenv()
    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        raise SystemExit("Xato: .env faylida EIA_API_KEY topilmadi")
    return api_key


def fetch_dataset(api_key, route, frequency, series, start):
    url = f"{API_BASE_URL}/{route}"
    params = {
        "api_key": api_key,
        "frequency": frequency,
        "data[0]": "value",
        "facets[series][]": series,
        "start": start,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": PAGE_SIZE,
    }

    all_records = []
    pages = []
    offset = 0

    while True:
        params["offset"] = offset
        response = requests.get(url, params=params, timeout=TIMEOUT)
        if response.status_code != 200:
            raise SystemExit(f"Xato: server {response.status_code} qaytardi. Javob: {response.text[:300]}")

        data = response.json()
        page = data["response"]["data"]
        total = int(data["response"]["total"])

        pages.append(data)
        all_records.extend(page)
        log.info(f"  sahifa: offset={offset}, keldi={len(page)}, jami={total}")

        offset += len(page)
        if not page or offset >= total:
            break

    return pages, all_records


def save_bronze(name, pages):
    bronze_dir = BASE_DIR / "data" / "bronze" / name
    bronze_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_path = bronze_dir / f"{name}_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    return file_path


def run():
    api_key = get_api_key()

    log.info("spot: yuklanmoqda...")
    pages, records = fetch_dataset(
        api_key=api_key,
        route="petroleum/pri/spt/data/",
        frequency="daily",
        series=["RWTC", "RBRTE", "EER_EPD2DXL0_PF4_Y35NY_DPG", "EER_EPD2DXL0_PF4_RGC_DPG"],
        start="2024-01-01",
    )
    saved_path = save_bronze("spot", pages)
    log.info(f"spot: {len(records)} qator, saqlandi: {saved_path.relative_to(BASE_DIR)}")

    log.info("retail: yuklanmoqda...")
    pages, records = fetch_dataset(
        api_key=api_key,
        route="petroleum/pri/gnd/data/",
        frequency="weekly",
        series=[
            "EMD_EPD2DXL0_PTE_NUS_DPG",
            "EMD_EPD2DXL0_PTE_R10_DPG",
            "EMD_EPD2DXL0_PTE_R1X_DPG",
            "EMD_EPD2DXL0_PTE_R1Y_DPG",
            "EMD_EPD2DXL0_PTE_R1Z_DPG",
            "EMD_EPD2DXL0_PTE_R20_DPG",
            "EMD_EPD2DXL0_PTE_R30_DPG",
            "EMD_EPD2DXL0_PTE_R40_DPG",
            "EMD_EPD2DXL0_PTE_R50_DPG",
            "EMD_EPD2DXL0_PTE_R5XCA_DPG",
            "EMD_EPD2DXL0_PTE_SCA_DPG",
        ],
        start="2024-01-01",
    )
    saved_path = save_bronze("retail", pages)
    log.info(f"retail: {len(records)} qator, saqlandi: {saved_path.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()