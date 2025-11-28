# Upgrade Script untuk Dependencies
# Jalankan script ini untuk upgrade dependencies yang deprecated

Write-Host "🔧 Upgrading Python Dependencies..." -ForegroundColor Cyan
Write-Host ""

# Uninstall deprecated aioredis
Write-Host "📦 Uninstalling deprecated aioredis..." -ForegroundColor Yellow
pip uninstall -y aioredis

# Install new dependencies
Write-Host "📦 Installing new dependencies..." -ForegroundColor Yellow
pip install python-dotenv==1.0.0
pip install pytz==2024.1
pip install "redis[asyncio]==5.0.1"

Write-Host ""
Write-Host "✅ Dependencies upgraded successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy .env.example to .env"
Write-Host "2. Edit .env and set your SECRET_KEY"
Write-Host "3. Configure database credentials in .env"
Write-Host "4. Run: python app.py"
Write-Host ""
