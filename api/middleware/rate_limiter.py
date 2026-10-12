"""
api/middleware/rate_limiter.py
In-memory sliding window rate limiter for QuantumGuard API.
Protects CPU-heavy quantum simulation endpoints (L=1024) from denial of service.
"""

import time
from collections import defaultdict
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Sliding window rate limiter middleware.
    Rate limits high-frequency requests per client IP address.
    """

    def __init__(self, app, max_requests_per_minute: int = 120):
        super().__init__(app)
        self.max_requests = max_requests_per_minute
        self.window_seconds = 60.0
        self.request_records: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Only rate limit compute-heavy endpoints
        path = request.url.path
        if path.startswith("/api/simulate") or path.startswith("/api/benchmark") or path.startswith("/api/attack-matrix"):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            cutoff = now - self.window_seconds

            # Filter old timestamps
            self.request_records[client_ip] = [t for t in self.request_records[client_ip] if t > cutoff]

            if len(self.request_records[client_ip]) >= self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": f"Too many quantum simulation requests. Limit is {self.max_requests} requests per minute.",
                        "retry_after_seconds": int(self.window_seconds - (now - self.request_records[client_ip][0]))
                    }
                )

            self.request_records[client_ip].append(now)

        response = await call_next(request)
        return response
