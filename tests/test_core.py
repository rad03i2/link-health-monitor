import json

import pytest

from link_health_monitor.core import LinkResult, json_report, load_targets, summarize, validate_url


def result(url="https://example.com", healthy=True, redirected=False):
    return LinkResult(url, url, 200, 12.5, healthy, redirected)


def test_validate_url_accepts_http_https_and_unicode_path():
    assert validate_url(" https://example.com/مرحبا ") == "https://example.com/مرحبا"
    assert validate_url("http://localhost:8000") == "http://localhost:8000"

@pytest.mark.parametrize("value", ["ftp://example.com", "example.com", "https://", "file:///tmp/a"])
def test_validate_url_rejects_non_http(value):
    with pytest.raises(ValueError):
        validate_url(value)


def test_validate_url_rejects_embedded_credentials():
    with pytest.raises(ValueError):
        validate_url("https://user:secret@example.com")


def test_summary_counts_health_redirects_and_latency():
    rows = [result(), LinkResult("https://a.test", "https://b.test", 301, 27.5, False, True)]
    assert summarize(rows) == {"total": 2, "healthy": 1, "unhealthy": 1, "redirected": 1, "average_latency_ms": 20.0}


def test_json_report_is_machine_readable_and_unicode_safe():
    data = json.loads(json_report([result("https://example.com/مرحبا")]))
    assert data["summary"]["healthy"] == 1
    assert data["results"][0]["url"].endswith("مرحبا")


def test_load_targets_ignores_comments_blank_lines_and_dedicated_file(tmp_path):
    target = tmp_path / "targets.txt"
    target.write_text("# prod\n\nhttps://example.com\nhttp://localhost:8080\n", encoding="utf-8")
    assert load_targets(target) == ["https://example.com", "http://localhost:8080"]


def test_empty_target_file_is_rejected(tmp_path):
    target = tmp_path / "targets.txt"
    target.write_text("# only comments\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_targets(target)
