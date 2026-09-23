from __future__ import annotations

import json
import socket
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener

USER_AGENT = "link-health-monitor/1.0 (+https://github.com/rad03i2/link-health-monitor)"


@dataclass(frozen=True)
class LinkResult:
    url: str
    final_url: str | None
    status: int | None
    latency_ms: float | None
    healthy: bool
    redirected: bool
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def validate_url(url: str) -> str:
    value = url.strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"invalid HTTP(S) URL: {url!r}")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URLs containing embedded credentials are not allowed")
    return value


def check_link(url: str, *, timeout: float = 10.0, method: str = "HEAD", max_latency_ms: float | None = None) -> LinkResult:
    url = validate_url(url)
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")
    method = method.upper()
    if method not in {"HEAD", "GET"}:
        raise ValueError("method must be HEAD or GET")
    if max_latency_ms is not None and max_latency_ms < 0:
        raise ValueError("max_latency_ms cannot be negative")

    request = Request(url, method=method, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    start = time.perf_counter()
    try:
        with build_opener().open(request, timeout=timeout) as response:
            latency = round((time.perf_counter() - start) * 1000, 2)
            status = response.getcode()
            final_url = response.geturl()
            status_ok = 200 <= status < 400
            latency_ok = max_latency_ms is None or latency <= max_latency_ms
            return LinkResult(url, final_url, status, latency, status_ok and latency_ok, final_url != url)
    except HTTPError as exc:
        latency = round((time.perf_counter() - start) * 1000, 2)
        return LinkResult(url, exc.geturl(), exc.code, latency, False, exc.geturl() != url, f"HTTP {exc.code}")
    except (URLError, TimeoutError, socket.timeout, OSError) as exc:
        latency = round((time.perf_counter() - start) * 1000, 2)
        reason = getattr(exc, "reason", exc)
        return LinkResult(url, None, None, latency, False, False, str(reason))


def check_links(urls: Iterable[str], **kwargs) -> list[LinkResult]:
    return [check_link(url, **kwargs) for url in urls]


def load_targets(path: str | Path) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    targets = []
    for line in lines:
        value = line.strip()
        if value and not value.startswith("#"):
            targets.append(validate_url(value))
    if not targets:
        raise ValueError("target file contains no URLs")
    return targets


def summarize(results: Iterable[LinkResult]) -> dict:
    rows = list(results)
    healthy = sum(item.healthy for item in rows)
    redirected = sum(item.redirected for item in rows)
    latencies = [item.latency_ms for item in rows if item.latency_ms is not None]
    return {
        "total": len(rows),
        "healthy": healthy,
        "unhealthy": len(rows) - healthy,
        "redirected": redirected,
        "average_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
    }


def json_report(results: Iterable[LinkResult]) -> str:
    rows = list(results)
    return json.dumps({"summary": summarize(rows), "results": [r.to_dict() for r in rows]}, ensure_ascii=False, indent=2)
