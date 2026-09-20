#!/bin/bash
# SmartGrow Azure Deployment Script (PoC)
# Run this script directly in your terminal. Passwords will be prompted securely.

# Exit immediately if any command fails
set -e

# 1. Variables
RESOURCE_GROUP="smartgrow-rg"
LOCATION="francecentral"
ACR_NAME="smartgrowacr$RANDOM"
DB_SERVER_NAME="smartgrow-db-$RANDOM"
DB_ADMIN_USER="sensordb_admin"
DB_NAME="sensordb"
DNS_NAME_LABEL="smartgrow-backend-$RANDOM"

echo "=== SmartGrow Azure Pre-Flight Checks ==="
if ! command -v az &> /dev/null; then
    echo "ERROR: 'az' CLI is not installed."
    exit 1
fi

if ! az account show >/dev/null 2>&1; then
    echo "ERROR: You are not logged into Azure CLI. Run 'az login' first."
    exit 1
fi

echo "Verifying region and provider availability..."
if ! az account list-locations --query "[].name" -o tsv | grep -q "^${LOCATION}$"; then
    echo "ERROR: Region $LOCATION is invalid or unavailable."
    exit 1
fi

# Register resource providers
az provider register --namespace Microsoft.ContainerInstance
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.ContainerRegistry

echo "Querying available SKUs in $LOCATION..."
az postgres flexible-server list-skus --location $LOCATION --query "[?name=='Standard_B1ms'] | [0].{SKU:name, Tier:tier, Available:!isNull(name)}" -o table

echo ""
echo "=== Pre-flight complete. ==="
echo ""
read -p "Do you want to proceed with resource creation? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Deployment aborted."
    exit 1
fi

echo "=== Secure Credential Input ==="
echo "Please enter the passwords for your new services. Characters will be hidden."
echo "(Avoid using the '\$' character in passwords to prevent templating issues)"
echo ""

read -rs -p "Enter PostgreSQL Admin Password: " DB_ADMIN_PASSWORD
echo ""
read -rs -p "Confirm PostgreSQL Admin Password: " DB_ADMIN_PASSWORD_CONFIRM
echo ""

if [ "$DB_ADMIN_PASSWORD" != "$DB_ADMIN_PASSWORD_CONFIRM" ]; then
    echo "ERROR: PostgreSQL passwords do not match."
    exit 1
fi

read -rs -p "Enter MQTT Password for Pico W: " MQTT_PASSWORD
echo ""
read -rs -p "Confirm MQTT Password: " MQTT_PASSWORD_CONFIRM
echo ""

if [ "$MQTT_PASSWORD" != "$MQTT_PASSWORD_CONFIRM" ]; then
    echo "ERROR: MQTT passwords do not match."
    exit 1
fi

export POSTGRES_PASSWORD="$DB_ADMIN_PASSWORD"
export MQTT_PASSWORD="$MQTT_PASSWORD"

echo ""
echo "=== 1. Handling Resource Group ==="
if az group show --name $RESOURCE_GROUP > /dev/null 2>&1; then
    echo "Resource group $RESOURCE_GROUP already exists. Reusing it."
else
    echo "Resource group $RESOURCE_GROUP does not exist. Creating it in $LOCATION..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
fi

echo "=== 2. Creating Azure Container Registry (ACR) ==="
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --location $LOCATION --sku Basic --admin-enabled true

echo "=== 3. Building and Pushing Images to ACR ==="
az acr build --registry $ACR_NAME --image mosquitto:latest -f src_pipeline/dockerfiles/mosquitto.dockerfile .
az acr build --registry $ACR_NAME --image consumer:latest -f src_pipeline/dockerfiles/consumer.dockerfile .

echo "=== 4. Getting ACR Credentials ==="
export ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" --output tsv)
export ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

echo "=== 5. Creating Azure Database for PostgreSQL Flexible Server ==="
az postgres flexible-server create \
    --resource-group $RESOURCE_GROUP \
    --name $DB_SERVER_NAME \
    --location $LOCATION \
    --admin-user $DB_ADMIN_USER \
    --admin-password "$DB_ADMIN_PASSWORD" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 16 \
    --public-access all

echo "=== 6. Configuring TimescaleDB Extension ==="
az postgres flexible-server parameter set --resource-group $RESOURCE_GROUP --server-name $DB_SERVER_NAME --name azure.extensions --value timescaledb
az postgres flexible-server parameter set --resource-group $RESOURCE_GROUP --server-name $DB_SERVER_NAME --name shared_preload_libraries --value timescaledb
az postgres flexible-server restart --resource-group $RESOURCE_GROUP --name $DB_SERVER_NAME

echo "=== 7. Creating Database and Restricting Firewall ==="
az postgres flexible-server db create --resource-group $RESOURCE_GROUP --server-name $DB_SERVER_NAME --database-name $DB_NAME

# Temporarily disable set -e because the rule might not exist on a fresh DB, causing a safe failure
set +e
az postgres flexible-server firewall-rule delete --resource-group $RESOURCE_GROUP --server-name $DB_SERVER_NAME --rule-name AllowAll --yes 2>/dev/null
set -e

# Security Note: This rule (0.0.0.0 to 0.0.0.0) allows ANY Azure service (even from other Azure customers in different subscriptions) 
# to reach the DB firewall endpoint. This is a PoC compromise to avoid complex VNet injection. 
# A production system should use restricted private networking.
az postgres flexible-server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME \
    --rule-name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

echo "=== 8. Initializing TimescaleDB on Server ==="
DB_FQDN="${DB_SERVER_NAME}.postgres.database.azure.com"

echo "Running one-time CREATE EXTENSION for TimescaleDB via psql..."
if ! command -v psql &> /dev/null; then
    echo "ERROR: 'psql' is required to initialize the database but is not installed."
    exit 1
fi

export PGPASSWORD="$DB_ADMIN_PASSWORD"
psql "host=$DB_FQDN port=5432 dbname=$DB_NAME user=$DB_ADMIN_USER sslmode=require" -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
echo "TimescaleDB extension successfully created!"

echo "=== 9. Deploying Azure Container Instances (ACI) ==="
export DB_HOST=$DB_FQDN
export POSTGRES_USER=$DB_ADMIN_USER
export DNS_NAME_LABEL=$DNS_NAME_LABEL
export ACR_NAME=$ACR_NAME

envsubst '${ACR_NAME} ${ACR_USERNAME} ${ACR_PASSWORD} ${DB_HOST} ${POSTGRES_USER} ${POSTGRES_PASSWORD} ${MQTT_PASSWORD} ${DNS_NAME_LABEL}' < src_pipeline/aci-deploy.yaml.template > src_pipeline/aci-deploy.yaml

az container create --resource-group $RESOURCE_GROUP --file src_pipeline/aci-deploy.yaml

# Cleanup temporary secrets file
rm src_pipeline/aci-deploy.yaml

echo "=== Deployment Complete ==="
echo "MQTT Broker Address: ${DNS_NAME_LABEL}.${LOCATION}.azurecontainer.io"
echo "Database Address: ${DB_FQDN}"
