"""Shared HTTP client with retry logic and exponential backoff."""

import time

import httpx
from loguru import logger

MAX_RETRIES = 3
BACKOFF_SECONDS = 2
REQUEST_TIMEOUT = 60


def fetch_json(url: str, params: dict | None = None) -> dict | list:
    """GET a URL and return parsed JSON, with retries on failure.

    Parameters
    ----------
    url : str
        The full URL to request.
    params : dict, optional
        Query parameters to include.

    Returns
    -------
    dict | list
        Parsed JSON response.

    Raises
    ------
    RuntimeError
        If all retry attempts fail.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = httpx.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.warning(f"Attempt {attempt}/{MAX_RETRIES} failed: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_SECONDS ** attempt)
    raise RuntimeError(f"All {MAX_RETRIES} attempts failed for {url}")
