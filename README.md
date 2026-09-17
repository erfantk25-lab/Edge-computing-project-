# πCo – Smart Plant Environmental Monitor (Edge IoT)

An edge computing telemetry and alerting pipeline built with the Raspberry Pi Pico W. The device monitors climate and lighting conditions, evaluates environmental thresholds locally on edge, drives localized alarms, and streams readings to a containerized TimescaleDB and Grafana stack (deployable locally or to Azure).

---

## Architecture

```text
[ Pico W (DHT11, LDR, LCD/OLED, Buzzer/LED) ]
                      │
                      ▼ (Wi-Fi / JSON MQTT)
             [ Mosquitto Broker ]
                      │
                      ▼
              [ Python Consumer ]
                      │
                      ▼
                [ TimescaleDB ]
                      │
                      ▼
              [ Grafana Dashboard ]
```

Pipeline flow: Edge sensing & alert → MQTT ingestion → TimescaleDB storage → Grafana visualization.

## Project Structure

```
├── docs/
│   └── way-of-working.md        # Agile process, branching, and PR rules
├── src_pico/
│   ├── umqtt/simple.py          # MicroPython MQTT client
│   ├── wifi_credentials.json    # Local network secrets (gitignored)
│   ├── wifi.py                  # RP2 Wi-Fi initialization helper
│   └── main.py                  # Measurement loop, alert logic & publisher
├── src_pipeline/
│   ├── dockerfiles/
│   │   └── consumer.dockerfile  # Optimized uv-based consumer image
│   ├── utils/
│   │   └── connect_postgres.py  # Parameterized TimescaleDB client
│   ├── consumer.py              # MQTT subscriber & database ingestion worker
│   ├── docker-compose.yaml      # Mosquitto, TimescaleDB, consumer & Grafana
│   ├── .env.example
│   └── .env                     # Local secrets (gitignored)
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
```
