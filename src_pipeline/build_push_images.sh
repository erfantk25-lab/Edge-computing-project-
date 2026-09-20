#!/bin/bash
set -e

echo "=== SmartGrow Local Build and Push Script ==="

# 1. Load environment variables
if [ ! -f "src_pipeline/.env" ]; then
    echo "ERROR: src_pipeline/.env file not found!"
    exit 1
fi

set -a
source src_pipeline/.env
set +a

if [ -z "$ACR_NAME" ]; then
    echo "ERROR: ACR_NAME is missing from .env"
    exit 1
fi

ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"

# 2. Verify Docker is available
echo "=== Verifying Docker ==="
if ! command -v docker &> /dev/null; then
    echo "ERROR: 'docker' command not found. Please install Docker Desktop and ensure it is running."
    exit 1
fi
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

# 3. Verify Azure Login
echo "=== Verifying Azure Login ==="
if ! az account show > /dev/null 2>&1; then
    echo "You are not logged into Azure CLI. Please run 'az login' first."
    exit 1
fi

# 4. Log into Azure Container Registry
echo "=== Logging into ACR: $ACR_NAME ==="
az acr login --name "$ACR_NAME"

# 5. Build and Tag Images
echo "=== Building Mosquitto Image ==="
docker build -t "${ACR_LOGIN_SERVER}/smartgrow-mosquitto:latest" -f src_pipeline/dockerfiles/mosquitto.dockerfile .

echo "=== Building Consumer Image ==="
docker build -t "${ACR_LOGIN_SERVER}/smartgrow-consumer:latest" -f src_pipeline/dockerfiles/consumer.dockerfile .

# 6. Push Images to ACR
echo "=== Pushing Images to ACR ==="
docker push "${ACR_LOGIN_SERVER}/smartgrow-mosquitto:latest"
docker push "${ACR_LOGIN_SERVER}/smartgrow-consumer:latest"

# 7. Verify images in ACR
echo "=== Verifying Images in ACR ==="
az acr repository list --name "$ACR_NAME" --output table

echo "=== Build and Push Complete ==="
echo "You can now run 'bash src_pipeline/deploy_aci.sh' to deploy to Azure Container Instances."
