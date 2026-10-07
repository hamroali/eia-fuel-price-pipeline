"""Transform: Bronze JSON'dan toza jadval yasash va Silver qatlamga saqlash."""
import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)


def load_latest_bronze(name):
    bronze_dir = BASE_DIR / "data" / "bronze" / name
    files = sorted(bronze_dir.glob(f"{name}_*.json"))
    if not files:
        raise SystemExit(f"Xato: {bronze_dir} ichida fayl topilmadi")
    latest = files[-1]

    with open(latest, encoding="utf-8") as f:
        pages = json.load(f)

    records = []
    for page in pages:
        records.extend(page["response"]["data"])

    print(f"{name}: {latest.name} o'qildi, {len(records)} qator")
    return pd.DataFrame(records)

KEEP_COLUMNS = {
    "period": "date",
    "series": "series_id",
    "duoarea": "area_code",
    "value": "price",
    "units": "unit",
}


def clean(df):
    df = df[list(KEEP_COLUMNS)].rename(columns=KEEP_COLUMNS)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["name"] = df["series_id"].map(SERIES_NAMES)
    return df

def check_quality(df, name):
    dupes = df.duplicated(subset=["date", "series_id"]).sum()
    nulls = df.isna().sum().sum()
    if dupes or nulls:
        raise SystemExit(f"Xato: {name} sifat tekshiruvidan o'tmadi: dublikat={dupes}, bo'sh qiymat={nulls}")
    print(f"{name}: sifat tekshiruvi o'tdi ({len(df)} qator)")


def save_silver(df, name):
    silver_dir = BASE_DIR / "data" / "silver"
    silver_dir.mkdir(parents=True, exist_ok=True)
    file_path = silver_dir / f"{name}.csv"
    df.sort_values(["series_id", "date"]).to_csv(file_path, index=False)
    return file_path

SERIES_NAMES = {
    # Spot narxlar
    "RWTC": "WTI Crude",
    "RBRTE": "Brent Crude",
    "EER_EPD2DXL0_PF4_Y35NY_DPG": "ULSD NY Harbor",
    "EER_EPD2DXL0_PF4_RGC_DPG": "ULSD Gulf Coast",
    # Chakana dizel narxlari
    "EMD_EPD2DXL0_PTE_NUS_DPG": "U.S. Average",
    "EMD_EPD2DXL0_PTE_R10_DPG": "East Coast (PADD 1)",
    "EMD_EPD2DXL0_PTE_R1X_DPG": "New England (PADD 1A)",
    "EMD_EPD2DXL0_PTE_R1Y_DPG": "Central Atlantic (PADD 1B)",
    "EMD_EPD2DXL0_PTE_R1Z_DPG": "Lower Atlantic (PADD 1C)",
    "EMD_EPD2DXL0_PTE_R20_DPG": "Midwest (PADD 2)",
    "EMD_EPD2DXL0_PTE_R30_DPG": "Gulf Coast (PADD 3)",
    "EMD_EPD2DXL0_PTE_R40_DPG": "Rocky Mountain (PADD 4)",
    "EMD_EPD2DXL0_PTE_R50_DPG": "West Coast (PADD 5)",
    "EMD_EPD2DXL0_PTE_R5XCA_DPG": "West Coast excl. California",
    "EMD_EPD2DXL0_PTE_SCA_DPG": "California",
}

if __name__ == "__main__":
    for name in ["spot", "retail"]:
        df = load_latest_bronze(name)
        df = clean(df)
        check_quality(df, name)
        saved_path = save_silver(df, name)
        print(f"{name}: saqlandi -> {saved_path.relative_to(BASE_DIR)}")