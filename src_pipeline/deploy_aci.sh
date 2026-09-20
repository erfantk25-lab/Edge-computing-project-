#!/bin/bash
set -e

echo "=== SmartGrow ACI Deployment Script (PoC Ephemeral Database) ==="

# 1. Load environment variables
if [ ! -f "src_pipeline/.env" ]; then
    echo "ERROR: src_pipeline/.env file not found!"
    echo "Please copy src_pipeline/.env.example to src_pipeline/.env and fill in the values."
    exit 1
fi

set -a
source src_pipeline/.env
set +a

# Validate essential variables
if [ -z "$ACR_NAME" ] || [ -z "$DNS_NAME_LABEL" ]; then
    echo "ERROR: ACR_NAME or DNS_NAME_LABEL is missing from .env"
    exit 1
fi

# 2. Check Azure login
echo "=== Verifying Azure Login ==="
if ! az account show > /dev/null 2>&1; then
    echo "You are not logged into Azure. Please run 'az login' first."
    exit 1
fi

# 3. Create Resource Group
echo "=== Creating Resource Group: $RESOURCE_GROUP ==="
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" -o none
echo "Resource Group created."

# 4. Create Azure Container Registry (ACR)
echo "=== Creating Azure Container Registry: $ACR_NAME ==="
az acr create --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --sku Basic --admin-enabled true -o none
echo "ACR created."

# 5. Build and Push Images using ACR Tasks
echo "=== Building and Pushing Images to ACR ==="
echo "Building mosquitto image..."
az acr build --registry "$ACR_NAME" --image smartgrow-mosquitto:latest -f src_pipeline/dockerfiles/mosquitto.dockerfile .

echo "Building consumer image..."
az acr build --registry "$ACR_NAME" --image smartgrow-consumer:latest -f src_pipeline/dockerfiles/consumer.dockerfile .

# 6. Retrieve ACR Credentials
echo "=== Retrieving ACR Credentials ==="
export ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query "username" --output tsv)
export ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" --output tsv)

# 7. Generate ACI YAML Configuration
echo "=== Generating ACI Configuration ==="
# Create a secure temporary file outside the workspace
ACI_YAML=$(mktemp)
# Ensure the temporary file is deleted when the script exits (success or failure)
trap 'rm -f "$ACI_YAML"' EXIT

# Using envsubst to replace variables in the template
envsubst < src_pipeline/aci.yaml.template > "$ACI_YAML"

# 8. Deploy to Azure Container Instances
echo "=== Deploying Azure Container Instances (ACI) ==="
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --file "$ACI_YAML"

echo "=== Deployment Complete! ==="
echo "Your MQTT broker is accessible at: ${DNS_NAME_LABEL}.${LOCATION}.azurecontainer.io"
echo "Port: 1883"
echo "WARNING: For this PoC, TimescaleDB storage is ephemeral."
echo "If the ACI group is restarted, all database data will be lost."
