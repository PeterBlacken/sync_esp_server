"""Simple HTTP time-sync server for ESP32 clients.

The server offers a single endpoint that returns the current server time.
Clients can use it to estimate offset/round-trip time and align clocks on
an isolated network without relying on public NTP.
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple

logger = logging.getLogger(__name__)


class TimeRequestHandler(BaseHTTPRequestHandler):
    """Serves the current UTC time as JSON.

    Response example:
    ```json
    {
        "iso_timestamp": "2024-05-01T12:00:00.123Z",
        "unix_epoch_ms": 1714564800123,
        "monotonic_hint_ms": 987654321.0
    }
    ```
    """

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler naming)
        """Return the current server time.

        Additional paths can be added later; for now we only serve "/time".
        """

        if self.path not in {"/", "/time"}:
            self._send_json({"error": "not found"}, status=404)
            return

        now = datetime.now(timezone.utc)
        # Using monotonic time as a hint lets clients compute round-trip offset
        # between request and response if they measure their own monotonic clocks.
        payload = {
            "iso_timestamp": now.isoformat(timespec="milliseconds"),
            "unix_epoch_ms": int(now.timestamp() * 1000),
            "monotonic_hint_ms": self.server.monotonic_fn() * 1000.0,
        }
        logger.info("Served time payload: %s", payload)
        self._send_json(payload)

    # Silence default logging to stderr; we use the module logger instead.
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        logger.debug("%s - - %s", self.address_string(), format % args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local ESP32 time sync server")
    parser.add_argument("--host", default="0.0.0.0", help="Host/IP to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity",
    )
    return parser.parse_args()


def build_server(host: str, port: int) -> Tuple[HTTPServer, logging.Logger]:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logger.setLevel(logging.INFO)

    # Attach a monotonic clock provider to the server instance so handlers can use it.
    server = HTTPServer((host, port), TimeRequestHandler)
    server.monotonic_fn = getattr(__import__("time"), "monotonic")
    return server, logger


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=args.log_level, format="[%(levelname)s] %(message)s")
    logger.setLevel(args.log_level)

    server, log = build_server(args.host, args.port)
    log.info("Starting time-sync server on %s:%s", args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
