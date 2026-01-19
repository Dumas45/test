import asyncio
import logging
import time
from typing import Optional

import requests

log = logging.getLogger(__name__)


def io_bound(duration: float = 1.0, url: Optional[str] = None):
    """Simulate an IO-bound operation using HTTP request with timeout."""
    if url is None:
        # Default URL that introduces a delay
        url = "https://httpbin.org/delay/10"

    try:
        requests.get(url, timeout=duration)
    except requests.Timeout:
        pass
    except requests.RequestException as e:
        log.error("An error occurred: %s", e)


async def io_bound_async(duration: float = 1.0, url: Optional[str] = None):
    await asyncio.to_thread(io_bound, duration, url)


def cpu_bound(duration: float = 1.0, factor: float = 1.0):
    """
    Simulate CPU-bound dummy operation.
    
    Returns calculated value, that depends on the factor.

    """
    start_time = time.time()
    result = 0.0
    # Perform a computation-heavy operation until `duration` seconds have passed
    while time.time() - start_time < duration:
        result += factor ** 2  # Example computation, squaring the 'factor'
        result %= 1000000.0  # Keep result manageable

    return result


async def cpu_bound_async(duration: float = 1.0, factor: float = 1.0):
    return await asyncio.to_thread(cpu_bound, duration, factor)
