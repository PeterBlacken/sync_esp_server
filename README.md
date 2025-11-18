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

## Troubleshooting LAN access (connection refused)

If the ESP reports `connection refused` while a browser on the same machine can reach the server, check the following:

1. **Bind to the LAN interface.** Passing `--host 0.0.0.0` (or your machine's LAN IP) allows remote clients; binding to `127.0.0.1`/`localhost` blocks LAN access.
2. **Confirm the port is listening.** While the server is running, `ss -ltnp | grep :8000` should show a listener on the chosen port. If nothing is listening, the ESP will see a refusal.
3. **Allow the port through the firewall.** On Debian/Ubuntu with UFW, `sudo ufw allow 8000/tcp` (or temporarily `ufw disable`) lets LAN clients connect. On firewalld-based systems, use `sudo firewall-cmd --add-port=8000/tcp`.
4. **Same WiFi / no client isolation.** Ensure the server host and ESP are on the same subnet/VLAN and that your AP/hotspot does not enable client isolation/guest-mode blocking.
5. **Use a numeric IP.** Set `SERVER_HOST` in `main/main.ino` to the server's LAN IP to avoid DNS resolution issues.
