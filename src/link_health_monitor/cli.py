from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import check_links, json_report, load_targets, summarize, validate_url


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="link-health", description="Check HTTP/HTTPS link health without external services.")
    p.add_argument("urls", nargs="*", help="HTTP/HTTPS URLs to check")
    p.add_argument("-f", "--file", help="UTF-8 file containing one URL per line")
    p.add_argument("--timeout", type=float, default=10.0, help="per-request timeout in seconds (default: 10)")
    p.add_argument("--method", choices=["HEAD", "GET"], default="HEAD", help="HTTP method (default: HEAD)")
    p.add_argument("--max-latency", type=float, metavar="MS", help="mark responses slower than this unhealthy")
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    p.add_argument("--output", help="write report to a UTF-8 file")
    p.add_argument("--fail-on-redirect", action="store_true", help="return exit code 1 when any URL redirects")
    p.add_argument("--version", action="version", version=f"link-health-monitor {__version__} — Radwan Abdulhadi Ahmed / @rad03i2")
    return p


def _text_report(results) -> str:
    lines = []
    for r in results:
        state = "OK" if r.healthy else "FAIL"
        status = r.status if r.status is not None else "-"
        latency = f"{r.latency_ms:.2f} ms" if r.latency_ms is not None else "-"
        suffix = f" -> {r.final_url}" if r.redirected and r.final_url else ""
        error = f" | {r.error}" if r.error else ""
        lines.append(f"[{state}] {status} | {latency} | {r.url}{suffix}{error}")
    s = summarize(results)
    lines.append(f"\nTotal: {s['total']} | Healthy: {s['healthy']} | Unhealthy: {s['unhealthy']} | Redirected: {s['redirected']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        urls = [validate_url(url) for url in args.urls]
        if args.file:
            urls.extend(load_targets(args.file))
        urls = list(dict.fromkeys(urls))
        if not urls:
            parser().error("provide at least one URL or --file")
        results = check_links(urls, timeout=args.timeout, method=args.method, max_latency_ms=args.max_latency)
        report = json_report(results) if args.json else _text_report(results)
        if args.output:
            Path(args.output).write_text(report + "\n", encoding="utf-8")
        else:
            print(report)
        failed = any(not r.healthy for r in results)
        redirected = args.fail_on_redirect and any(r.redirected for r in results)
        return 1 if failed or redirected else 0
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
