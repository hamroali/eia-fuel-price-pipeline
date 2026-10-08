"""Gold: Silver'dan Power BI uchun tayyor star schema jadvallarini yasash."""
from pathlib import Path
import logging
import pandas as pd

# Sozlamalar
BASE_DIR = Path(__file__).resolve().parent.parent
log = logging.getLogger(__name__)
CONFIG_DIR = BASE_DIR / "config"
SILVER_DIR = BASE_DIR / "data" / "silver"
GOLD_DIR = BASE_DIR / "data" / "gold"


def build_dim_series():
    return pd.read_csv(CONFIG_DIR / "series.csv")


def build_dim_state(dim_series):
    dim = pd.read_csv(CONFIG_DIR / "state_regions.csv")

    map_ids = set(dim_series.loc[dim_series["is_map_region"], "series_id"])
    state_ids = set(dim["series_id"])

    unknown = state_ids - map_ids
    if unknown:
        raise SystemExit(f"Xato: shtatlar xarita hududi bo'lmagan seriyaga bog'langan: {unknown}")

    empty = map_ids - state_ids
    if empty:
        raise SystemExit(f"Xato: bu xarita hududlarida birorta ham shtat yo'q: {empty}")

    if dim["state_code"].duplicated().any():
        raise SystemExit("Xato: bir shtat bir necha marta uchrayapti")

    print(f"dim_state: {len(dim)} shtat, {len(map_ids)} xarita hududi, tekshiruvlar o'tdi")
    return dim
def load_silver(name):
    return pd.read_csv(SILVER_DIR / f"{name}.csv", parse_dates=["date"])


def build_fact_prices(df):
    fact = df[["date", "series_id", "price"]].sort_values(["series_id", "date"]).copy()
    fact["prev_price"] = fact.groupby("series_id")["price"].shift(1)
    fact["change"] = (fact["price"] - fact["prev_price"]).round(4)
    fact["change_pct"] = (fact["change"] / fact["prev_price"]).round(6)
    return fact
SPREAD_COLUMNS = {
    "RWTC": "wti",
    "RBRTE": "brent",
    "EER_EPD2DXL0_PF4_Y35NY_DPG": "ulsd_nyh_gal",
}


def build_fact_spreads(spot):
    wide = spot.pivot(index="date", columns="series_id", values="price")
    wide = wide[list(SPREAD_COLUMNS)].rename(columns=SPREAD_COLUMNS).reset_index()

    wide["ulsd_nyh_bbl"] = (wide["ulsd_nyh_gal"] * 42).round(2)
    wide["brent_wti_spread"] = (wide["brent"] - wide["wti"]).round(2)
    wide["crack_spread"] = (wide["ulsd_nyh_bbl"] - wide["wti"]).round(2)

    return wide.dropna(subset=["brent_wti_spread", "crack_spread"], how="all")

def save_gold(df, name):
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = GOLD_DIR / f"{name}.csv"
    df.to_csv(file_path, index=False)
    print(f"gold: {name} saqlandi ({len(df)} qator)")
    return file_path


def run():
    dim_series = build_dim_series()
    dim_state = build_dim_state(dim_series)
    save_gold(dim_series, "dim_series")
    save_gold(dim_state, "dim_state")

    spot = load_silver("spot")
    retail = load_silver("retail")
    save_gold(build_fact_prices(spot), "fact_spot_prices")
    save_gold(build_fact_prices(retail), "fact_retail_prices")
    save_gold(build_fact_spreads(spot), "fact_spreads")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()