#!/bin/sh
set -e

# Create a password file using environment variables
if [ -n "$MQTT_USER" ] && [ -n "$MQTT_PASSWORD" ]; then
    echo "Creating mosquitto password file for user: $MQTT_USER"
    mosquitto_passwd -c -b /mosquitto/config/password.txt "$MQTT_USER" "$MQTT_PASSWORD"
else
    echo "WARNING: MQTT_USER or MQTT_PASSWORD not set. Authentication might fail."
    touch /mosquitto/config/password.txt
fi

# Ensure mosquitto user owns the password file
chown mosquitto:mosquitto /mosquitto/config/password.txt

# Chain into the official mosquitto entrypoint for standard initialization
exec /docker-entrypoint.sh /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
