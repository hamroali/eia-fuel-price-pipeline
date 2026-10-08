"""Transform: Bronze JSON'dan toza jadval yasash va Silver qatlamga saqlash."""
import json
from pathlib import Path

import pandas as pd

# Sozlamalar
BASE_DIR = Path(__file__).resolve().parent.parent
SERIES_FILE = BASE_DIR / "config" / "series.csv"

KEEP_COLUMNS = {
    "period": "date",
    "series": "series_id",
    "duoarea": "area_code",
    "value": "price",
    "units": "unit",
}

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)


def load_series_names():
    series = pd.read_csv(SERIES_FILE)
    return dict(zip(series["series_id"], series["name"]))


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


def clean(df):
    df = df[list(KEEP_COLUMNS)].rename(columns=KEEP_COLUMNS)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["name"] = df["series_id"].map(load_series_names())
    return df


def check_quality(df, name):
    dupes = df.duplicated(subset=["date", "series_id"]).sum()
    nulls = df.isna().sum().sum()
    if dupes or nulls:
        print(df.isna().sum())
        raise SystemExit(f"Xato: {name} sifat tekshiruvidan o'tmadi: dublikat={dupes}, bo'sh qiymat={nulls}")
    print(f"{name}: sifat tekshiruvi o'tdi ({len(df)} qator)")

def save_silver(df, name):
    silver_dir = BASE_DIR / "data" / "silver"
    silver_dir.mkdir(parents=True, exist_ok=True)
    file_path = silver_dir / f"{name}.csv"
    df.sort_values(["series_id", "date"]).to_csv(file_path, index=False)
    return file_path


if __name__ == "__main__":
    for name in ["spot", "retail"]:
        df = load_latest_bronze(name)
        df = clean(df)
        check_quality(df, name)
        saved_path = save_silver(df, name)
        print(f"{name}: saqlandi -> {saved_path.relative_to(BASE_DIR)}")