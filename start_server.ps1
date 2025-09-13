Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  Skylark Academy Server Setup" -ForegroundColor Cyan  
Write-Host "=================================" -ForegroundColor Cyan

Write-Host "Setting environment variables..." -ForegroundColor Yellow
$env:AUTO_POPULATE_DB = "true"
$env:DB_NAME = "skylark_academy" 
$env:DB_USER = "root"
$env:DB_PASSWORD = "somrup7"
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"

Write-Host "Changing to source directory..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\src"

Write-Host "Installing required packages..." -ForegroundColor Yellow
pip install mysqlclient

Write-Host "`nStarting Django development server..." -ForegroundColor Green
Write-Host "✅ Database will be created automatically if needed!" -ForegroundColor Green
Write-Host "✅ Migrations will run automatically!" -ForegroundColor Green  
Write-Host "✅ Sample data will be populated automatically!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Server will be available at: http://127.0.0.1:8000" -ForegroundColor Magenta
Write-Host "⚙️  Admin panel at: http://127.0.0.1:8000/admin/" -ForegroundColor Magenta
Write-Host ""

python manage.py runserver