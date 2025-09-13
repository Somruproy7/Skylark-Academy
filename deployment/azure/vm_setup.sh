#!/bin/bash
# [STUDENT-ID: C4055929 - Ramanjaneyulu Reddy Avuduri] VM Setup Script

echo "🔧 Setting up Azure VM for Registration App..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# Install PostgreSQL (optional, for production)
echo "🗄️  Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /var/www/registration-app
sudo chown $USER:$USER /var/www/registration-app

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
cd /var/www/registration-app
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install django gunicorn whitenoise psycopg2-binary

# Create Django project structure
echo "🏗️  Creating Django project structure..."
mkdir -p config registration static media templates

# Create basic Django files
echo "📝 Creating Django configuration files..."

# Create manage.py
cat > manage.py << 'EOF'
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
Django>=4.2.0
gunicorn>=20.1.0
whitenoise>=6.5.0
psycopg2-binary>=2.9.0
dj-database-url>=1.0.0
EOF

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Create Gunicorn service
echo "🔧 Creating Gunicorn service..."
sudo tee /etc/systemd/system/registration-app.service > /dev/null << EOF
[Unit]
Description=Registration App Gunicorn
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/registration-app
Environment="PATH=/var/www/registration-app/venv/bin"
ExecStart=/var/www/registration-app/venv/bin/gunicorn --workers 3 --bind unix:/var/www/registration-app/registration-app.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/registration-app > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/registration-app;
    }

    location /media/ {
        root /var/www/registration-app;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/registration-app/registration-app.sock;
    }
}
EOF

# Enable the site
echo "🔗 Enabling Nginx site..."
sudo ln -sf /etc/nginx/sites-available/registration-app /etc/nginx/sites-enabled
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Start and enable services
echo "🚀 Starting services..."
sudo systemctl start registration-app
sudo systemctl enable registration-app
sudo systemctl restart nginx
sudo systemctl enable nginx

# Set proper permissions
echo "🔐 Setting permissions..."
sudo chown -R $USER:www-data /var/www/registration-app
sudo chmod -R 755 /var/www/registration-app

echo "✅ VM setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Upload your Django application code to /var/www/registration-app/"
echo "2. Copy your config/ and registration/ directories"
echo "3. Run: python manage.py collectstatic --noinput"
echo "4. Run: python manage.py migrate"
echo "5. Create superuser: python manage.py createsuperuser"
echo ""
echo "🌐 Your app will be available at: http://YOUR_VM_IP"
echo "🔧 Check service status: sudo systemctl status registration-app"
echo "📝 Check logs: sudo journalctl -u registration-app -f"
