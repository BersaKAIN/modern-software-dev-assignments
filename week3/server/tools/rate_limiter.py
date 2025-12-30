"""Rate limiting for Notion API requests."""

import asyncio
import time
from typing import Optional


class RateLimiter:
    """Token bucket rate limiter for API requests."""

    def __init__(
        self,
        requests_per_second: float = 3.0,
        warning_threshold: float = 0.8,
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum requests per second allowed
            warning_threshold: Threshold (0-1) at which to warn about approaching limit
        """
        self.requests_per_second = requests_per_second
        self.warning_threshold = warning_threshold
        self.tokens = requests_per_second
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        self.request_count = 0
        self.window_start = time.time()

    async def acquire(self) -> Optional[str]:
        """
        Acquire a token for making a request.

        Returns:
            Warning message if approaching rate limit, None otherwise
        """
        while True:
            async with self.lock:
                now = time.time()
                elapsed = now - self.last_update

                # Refill tokens based on elapsed time
                self.tokens = min(
                    self.requests_per_second,
                    self.tokens + elapsed * self.requests_per_second,
                )
                self.last_update = now

                # Check if we can make a request
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    self.request_count += 1

                    # Check if we're approaching the rate limit
                    window_elapsed = now - self.window_start
                    if window_elapsed > 0.1:  # Only calculate rate if at least 100ms passed
                        current_rate = self.request_count / window_elapsed
                        if current_rate >= self.requests_per_second * self.warning_threshold:
                            return (
                                f"Warning: Approaching rate limit. "
                                f"Current rate: {current_rate:.2f} req/s "
                                f"(limit: {self.requests_per_second} req/s)"
                            )

                    # Reset window every second
                    if window_elapsed >= 1.0:
                        self.request_count = 0
                        self.window_start = now

                    return None
                else:
                    # Need to wait for tokens to refill
                    wait_time = (1.0 - self.tokens) / self.requests_per_second

            # Release lock before sleeping
            await asyncio.sleep(wait_time)

    async def handle_rate_limit_error(self, retry_after: Optional[float] = None) -> None:
        """
        Handle a 429 rate limit error from the API.

        Args:
            retry_after: Optional retry-after value from the API response (in seconds)
        """
        if retry_after:
            wait_time = retry_after
        else:
            # Exponential backoff: wait 1s, 2s, 4s, etc.
            wait_time = min(2 ** (self.request_count % 5), 10.0)

        await asyncio.sleep(wait_time)

