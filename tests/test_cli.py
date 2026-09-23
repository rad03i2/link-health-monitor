from link_health_monitor import cli
from link_health_monitor.core import LinkResult


def test_cli_json_success(monkeypatch, capsys):
    monkeypatch.setattr(cli, "check_links", lambda urls, **kwargs: [LinkResult(urls[0], urls[0], 200, 5.0, True, False)])
    assert cli.main(["https://example.com", "--json"]) == 0
    assert '"healthy": 1' in capsys.readouterr().out


def test_cli_returns_one_for_unhealthy(monkeypatch):
    monkeypatch.setattr(cli, "check_links", lambda urls, **kwargs: [LinkResult(urls[0], None, None, 2.0, False, False, "offline")])
    assert cli.main(["https://example.com"]) == 1


def test_cli_fail_on_redirect(monkeypatch):
    monkeypatch.setattr(cli, "check_links", lambda urls, **kwargs: [LinkResult(urls[0], "https://www.example.com", 200, 3.0, True, True)])
    assert cli.main(["https://example.com", "--fail-on-redirect"]) == 1


def test_cli_writes_output(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "check_links", lambda urls, **kwargs: [LinkResult(urls[0], urls[0], 200, 1.0, True, False)])
    output = tmp_path / "report.txt"
    assert cli.main(["https://example.com", "--output", str(output)]) == 0
    assert "[OK]" in output.read_text(encoding="utf-8")
