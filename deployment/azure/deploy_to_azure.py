#!/usr/bin/env python3
"""
Automated deployment script for Azure App Service
"""

import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Azure CLI
    if not run_command("az --version", "Checking Azure CLI"):
        print("❌ Azure CLI not found. Please install it first:")
        print("   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    # Check if logged in to Azure
    if not run_command("az account show", "Checking Azure login"):
        print("❌ Not logged in to Azure. Please run 'az login' first")
        return False
    
    print("✅ All prerequisites met!")
    return True

def create_resource_group(resource_group, location):
    """Create Azure resource group"""
    print(f"🏗️  Creating resource group '{resource_group}' in {location}...")
    
    command = f"az group create --name {resource_group} --location {location}"
    if run_command(command, f"Creating resource group '{resource_group}'"):
        return True
    return False

def create_app_service_plan(plan_name, resource_group, location, sku="B1"):
    """Create Azure App Service plan"""
    print(f"📋 Creating App Service plan '{plan_name}'...")
    
    command = f"az appservice plan create --name {plan_name} --resource-group {resource_group} --location {location} --sku {sku} --is-linux"
    if run_command(command, f"Creating App Service plan '{plan_name}'"):
        return True
    return False

def create_web_app(app_name, resource_group, plan_name, runtime="PYTHON:3.9"):
    """Create Azure Web App"""
    print(f"🌐 Creating Web App '{app_name}'...")
    
    command = f"az webapp create --resource-group {resource_group} --plan {plan_name} --name {app_name} --runtime {runtime}"
    if run_command(command, f"Creating Web App '{app_name}'"):
        return True
    return False

def configure_web_app(app_name, resource_group):
    """Configure the web app settings"""
    print(f"⚙️  Configuring Web App '{app_name}'...")
    
    # Set startup command
    startup_command = "gunicorn --bind=0.0.0.0 --timeout 600 registrationApp.wsgi:application"
    command = f"az webapp config set --resource-group {resource_group} --name {app_name} --startup-file '{startup_command}'"
    run_command(command, "Setting startup command")
    
    # Enable continuous deployment
    command = f"az webapp deployment source config --resource-group {resource_group} --name {app_name} --repo-url https://github.com/YOUR_USERNAME/YOUR_REPO.git --branch main --manual-integration"
    run_command(command, "Configuring deployment source")
    
    # Set environment variables
    env_vars = [
        "DJANGO_SETTINGS_MODULE=registrationApp.production",
        "DEBUG=False",
        "ALLOWED_HOSTS=.azurewebsites.net"
    ]
    
    for env_var in env_vars:
        key, value = env_var.split('=', 1)
        command = f"az webapp config appsettings set --resource-group {resource_group} --name {app_name} --settings {key}='{value}'"
        run_command(command, f"Setting environment variable {key}")

def deploy_app(app_name, resource_group):
    """Deploy the application"""
    print(f"🚀 Deploying application to '{app_name}'...")
    
    # Build and deploy
    command = f"az webapp up --name {app_name} --resource-group {resource_group} --runtime 'PYTHON:3.9' --sku B1 --plan {app_name}-plan"
    if run_command(command, "Deploying application"):
        return True
    return False

def main():
    """Main deployment function"""
    print("🚀 Azure Deployment Script for University Registration System")
    print("=" * 60)
    
    # Configuration
    resource_group = "university-registration-rg"
    location = "eastus"  # Change to your preferred region
    plan_name = "university-registration-plan"
    app_name = "university-registration-app"  # Must be globally unique
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    print(f"\n📋 Deployment Configuration:")
    print(f"   Resource Group: {resource_group}")
    print(f"   Location: {location}")
    print(f"   App Service Plan: {plan_name}")
    print(f"   Web App: {app_name}")
    
    # Confirm deployment
    response = input("\n🤔 Proceed with deployment? (y/N): ")
    if response.lower() != 'y':
        print("❌ Deployment cancelled")
        sys.exit(0)
    
    # Create resources
    if not create_resource_group(resource_group, location):
        sys.exit(1)
    
    if not create_app_service_plan(plan_name, resource_group, location):
        sys.exit(1)
    
    if not create_web_app(app_name, resource_group, plan_name):
        sys.exit(1)
    
    configure_web_app(app_name, resource_group)
    
    if not deploy_app(app_name, resource_group):
        sys.exit(1)
    
    print("\n🎉 Deployment completed successfully!")
    print(f"🌐 Your app is available at: https://{app_name}.azurewebsites.net")
    print(f"🔧 Azure Portal: https://portal.azure.com")
    print(f"📊 Monitor your app: https://portal.azure.com/#@/resource/subscriptions/...")

if __name__ == "__main__":
    main()
