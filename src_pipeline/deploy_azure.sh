#!/bin/bash
# SmartGrow Azure Preflight Script
# This script ONLY verifies your Azure environment. It creates NO resources.

LOCATION="westeurope"
ACR_NAME="smartgrowacr$RANDOM"
DB_SERVER_NAME="smartgrow-db-$RANDOM"

echo "=== 1. Checking Azure CLI Login & Subscription ==="
if ! command -v az &> /dev/null; then
    echo "ERROR: 'az' CLI is not installed."
    exit 1
fi

if ! az account show >/dev/null 2>&1; then
    echo "ERROR: You are not logged into Azure CLI. Run 'az login' first."
    exit 1
fi
az account show --query "{SubscriptionName:name, SubscriptionID:id}" -o table

echo ""
echo "=== 2. Checking Region Availability ($LOCATION) ==="
az account list-locations --query "[?name=='$LOCATION'].{Region:name, DisplayName:displayName}" -o table

echo ""
echo "=== 3. Checking Required Resource Providers ==="
echo "Note: If any say 'NotRegistered', you must run 'az provider register -n <Namespace>'"
az provider show -n Microsoft.ContainerInstance --query "{Provider:namespace, State:registrationState}" -o table | sed -n '1,2p; 3p'
az provider show -n Microsoft.DBforPostgreSQL --query "{Provider:namespace, State:registrationState}" -o table | sed -n '3p'
az provider show -n Microsoft.ContainerRegistry --query "{Provider:namespace, State:registrationState}" -o table | sed -n '3p'

echo ""
echo "=== 4. Checking PostgreSQL Flexible Server & B1ms SKU ==="
echo "Querying available SKUs in $LOCATION..."
az postgres flexible-server list-skus --location $LOCATION --query "[?name=='Standard_B1ms'] | [0].{SKU:name, Tier:tier, Available:!isNull(name)}" -o table

echo ""
echo "=== 5. Verifying Resource Naming Rules ==="
echo "ACR Name: $ACR_NAME"
if [[ "$ACR_NAME" =~ ^[a-z0-9]{5,50}$ ]]; then echo "  [PASS] Alphanumeric only, 5-50 chars."; else echo "  [FAIL] Naming rule violation."; fi

echo "DB Server Name: $DB_SERVER_NAME"
if [[ "$DB_SERVER_NAME" =~ ^[a-z0-9-]{3,63}$ ]]; then echo "  [PASS] Lowercase alphanumeric and hyphens, 3-63 chars."; else echo "  [FAIL] Naming rule violation."; fi

echo ""
echo "Preflight complete. No resources were created."
