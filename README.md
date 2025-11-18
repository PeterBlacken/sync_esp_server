# sync_esp_server

Prototype setup for testing time synchronization between ESP32-S3 devices and a local Python server without relying on external NTP.

## Python time-sync server

Run the HTTP server from the `python` directory:

```bash
cd python
python main.py --host 0.0.0.0 --port 8000
```

The `/time` endpoint returns a JSON payload containing:
- ISO 8601 UTC timestamp with milliseconds
- Unix epoch in milliseconds
- A monotonic clock hint (milliseconds) to help estimate round-trip latency

## ESP32-S3 draft sketch

A starter sketch is available at `main/main.ino`. Update the WiFi credentials and the server host/port before flashing. The sketch connects to WiFi, queries `/time` periodically, and logs the payload so you can compute offsets and apply them to your own timekeeping logic.
