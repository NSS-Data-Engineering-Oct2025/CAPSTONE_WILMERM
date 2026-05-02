"""Quick smoke test for all APIs — run once to confirm keys and endpoints work."""

import httpx
from loguru import logger

from src.config import api_keys


def test_cdc() -> None:
    url = "https://data.cdc.gov/resource/hksd-2xuw.json"
    params = {"$limit": 1}
    r = httpx.get(url, params=params, timeout=60)
    logger.info(f"CDC status={r.status_code} rows={len(r.json())}")
    logger.info(f"CDC columns: {list(r.json()[0].keys())}")


def test_epa() -> None:
    url = "https://www.airnowapi.org/aq/observation/state/current/"
    params = {
        "format": "application/json",
        "stateCode": "TN",
        "API_KEY": api_keys.epa_airnow,
    }
    r = httpx.get(url, params=params, timeout=60, follow_redirects=True)
    logger.info(f"EPA status={r.status_code} content-type={r.headers.get('content-type')}")
    if "json" in r.headers.get("content-type", ""):
        logger.info(f"EPA rows={len(r.json())}")
        if r.json():
            logger.info(f"EPA columns: {list(r.json()[0].keys())}")
    else:
        logger.warning("EPA returned HTML — key may need activation at https://docs.airnowapi.org/")


def test_usda() -> None:
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"api_key": api_keys.usda, "query": "broccoli", "pageSize": 1}
    r = httpx.get(url, params=params, timeout=60)
    logger.info(f"USDA status={r.status_code}")
    if r.status_code == 200 and r.json().get("foods"):
        logger.info(f"USDA first food: {r.json()['foods'][0]['description']}")
    else:
        logger.info(f"USDA response: {r.text[:500]}")


def test_census() -> None:
    url = "https://api.census.gov/data/2022/acs/acs5"
    params = {
        "get": "NAME,B01001_001E",
        "for": "state:47",
        "key": api_keys.census,
    }
    r = httpx.get(url, params=params, timeout=60, follow_redirects=True)
    logger.info(f"Census status={r.status_code} content-type={r.headers.get('content-type')}")
    logger.info(f"Census response (first 500 chars): {r.text[:500]}")


if __name__ == "__main__":
    test_cdc()
    test_epa()
    test_usda()
    test_census()
    logger.info("All API tests passed.")
