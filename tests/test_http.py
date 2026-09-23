from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from link_health_monitor.core import check_link


class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
        elif self.path == "/missing":
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()

    def log_message(self, *args):
        pass


def serve():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_live_local_http_success_redirect_and_error():
    server, thread = serve()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        ok = check_link(base + "/ok")
        assert ok.healthy and ok.status == 200 and not ok.redirected
        redirect = check_link(base + "/redirect")
        assert redirect.healthy and redirect.status == 200 and redirect.redirected
        missing = check_link(base + "/missing")
        assert not missing.healthy and missing.status == 404 and missing.error == "HTTP 404"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_latency_threshold_can_mark_valid_response_unhealthy():
    server, thread = serve()
    try:
        result = check_link(f"http://127.0.0.1:{server.server_port}/ok", max_latency_ms=0)
        assert result.status == 200 and not result.healthy
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)
