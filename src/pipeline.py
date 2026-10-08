"""Pipeline: Extract -> Transform -> Gold bosqichlarini ketma-ket ishga tushirish."""
import logging
import sys
from pathlib import Path

import extract
import transform
import gold

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "pipeline.log"

log = logging.getLogger("pipeline")


def setup_logging():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)-9s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def run():
    log.info("=== Pipeline boshlandi ===")
    log.info("--- 1/3 Extract ---")
    extract.run()
    log.info("--- 2/3 Transform ---")
    transform.run()
    log.info("--- 3/3 Gold ---")
    gold.run()
    log.info("=== Pipeline muvaffaqiyatli tugadi ===")


if __name__ == "__main__":
    setup_logging()
    try:
        run()
    except SystemExit as e:
        log.error(f"Pipeline to'xtadi: {e}")
        sys.exit(1)
    except Exception:
        log.exception("Kutilmagan xato")
        sys.exit(1)
        