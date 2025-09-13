from django.apps import AppConfig
import os
import sys
from decouple import config


class RegistrationConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name = 'registration'
    _setup_complete = False  # Class variable to prevent multiple setups
    
    def ready(self):
        # import registration.signals  # Import signals when app is ready
        
        # Only run setup once and not during migrations
        if (not self._setup_complete and 
            'migrate' not in sys.argv and 
            'makemigrations' not in sys.argv):
            
            self._setup_complete = True
            self.setup_database()
    
    def setup_database(self):
        """Complete database setup including creation, migrations, and population"""
        try:
            print("🚀 Starting automatic database setup...")
            
            # Step 1: Create database if it doesn't exist (MySQL only)
            self.create_database_if_needed()
            
            # Step 2: Run migrations
            self.run_migrations()
            
            # Step 3: Populate database if enabled
            if config('AUTO_POPULATE_DB', default='false').lower() in ['true', '1', 'yes']:
                self.populate_database()
                
        except Exception as e:
            print(f"⚠️  Error during database setup: {e}")
            # Don't crash the app if setup fails
            pass
    
    def create_database_if_needed(self):
        """Create MySQL database if it doesn't exist"""
        try:
            from django.conf import settings
            import MySQLdb
            
            db_settings = settings.DATABASES['default']
            
            if db_settings['ENGINE'] == 'django.db.backends.mysql':
                print("🔧 Checking MySQL database...")
                
                # Connect to MySQL server without specifying database
                connection = MySQLdb.connect(
                    host=config('DB_HOST', default='localhost'),
                    user=config('DB_USER', default='root'),
                    passwd=config('DB_PASSWORD', default='somrup7'),
                    port=int(config('DB_PORT', default='3306'))
                )
                
                cursor = connection.cursor()
                database_name = config('DB_NAME', default='skylark_academy')
                
                # Check if database exists
                cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
                exists = cursor.fetchone()
                
                if not exists:
                    # Create database
                    cursor.execute(f"CREATE DATABASE {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    print(f"✅ Created MySQL database: {database_name}")
                else:
                    print(f"✅ MySQL database already exists: {database_name}")
                
                cursor.close()
                connection.close()
                
        except ImportError:
            print("⚠️  MySQLdb not installed. Install with: pip install mysqlclient")
        except Exception as e:
            print(f"⚠️  Error creating MySQL database: {e}")
    
    def run_migrations(self):
        """Run Django migrations"""
        try:
            from django.core.management import call_command
            
            print("🔄 Running database migrations...")
            call_command('migrate', verbosity=1)
            print("✅ Migrations completed successfully")
            
        except Exception as e:
            print(f"⚠️  Error running migrations: {e}")
            raise
    
    def populate_database(self):
        """Populate database with initial data"""
        try:
            from django.core.management import call_command
            from django.db import transaction
            
            print("🔄 Auto-populating database with sample data...")
            
            # Use transaction to ensure all-or-nothing population
            with transaction.atomic():
                # Populate courses first (dependencies)
                call_command('populate_courses', verbosity=1)
                print("✅ Courses populated successfully")
                
                # Then populate modules
                call_command('populate_data', verbosity=1)
                print("✅ Modules populated successfully")
                
            print("🎉 Database auto-population completed!")
            
        except Exception as e:
            print(f"⚠️  Error during auto-population: {e}")
            # Don't crash the app if population fails
            pass
