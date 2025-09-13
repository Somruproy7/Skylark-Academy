#!/bin/bash
# [STUDENT-ID: C4055929 - Ramanjaneyulu Reddy Avuduri] Azure VM Deployment Script

echo "🚀 Starting Azure VM Deployment for Registration App..."

# Set variables
RESOURCE_GROUP="dtl-2425-55-708564-af-c4055929-033092"
LOCATION="northeurope"
VM_NAME="raman-registration-vm"
ADMIN_USERNAME="azureuser"

echo "📋 Using Resource Group: $RESOURCE_GROUP"
echo "📍 Location: $LOCATION"
echo "🖥️  VM Name: $VM_NAME"

# Step 1: Set subscription
echo "🔑 Setting subscription..."
az account set --subscription "8fc122ca-79a2-4628-9c9a-69278b28526d"

# Step 2: Create VM
echo "🏗️  Creating Ubuntu VM..."
az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image "Canonical:0001-com-ubuntu-server-focal:20_04-lts:latest" \
  --size "Standard_B2s" \
  --admin-username $ADMIN_USERNAME \
  --generate-ssh-keys \
  --location $LOCATION

# Step 3: Open ports
echo "🔓 Opening HTTP and HTTPS ports..."
az vm open-port \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --port 80

az vm open-port \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --port 443

# Step 4: Get VM Public IP
echo "🌐 Getting VM Public IP..."
VM_IP=$(az vm show \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --show-details \
  --query publicIps \
  --output tsv)

echo "✅ VM created successfully!"
echo "🖥️  VM Name: $VM_NAME"
echo "🌐 Public IP: $VM_IP"
echo "👤 Admin Username: $ADMIN_USERNAME"
echo ""
echo "🔑 SSH Command: ssh $ADMIN_USERNAME@$VM_IP"
echo ""
echo "📋 Next steps:"
echo "1. SSH into your VM: ssh $ADMIN_USERNAME@$VM_IP"
echo "2. Run the setup script inside the VM"
echo "3. Upload your application code"
echo ""
echo "🎯 Deployment script completed!"
