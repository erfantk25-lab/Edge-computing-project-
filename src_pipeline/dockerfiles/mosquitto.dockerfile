FROM eclipse-mosquitto:latest

COPY src_pipeline/mosquitto/config/mosquitto.conf /mosquitto/config/mosquitto.conf
COPY src_pipeline/mosquitto/config/docker-entrypoint-custom.sh /mosquitto/config/docker-entrypoint-custom.sh

RUN chmod +x /mosquitto/config/docker-entrypoint-custom.sh

ENTRYPOINT ["/mosquitto/config/docker-entrypoint-custom.sh"]
