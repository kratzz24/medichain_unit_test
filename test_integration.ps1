# Test Firebase + Supabase Integration
Write-Host "🧪 Testing MediChain Firebase + Supabase Integration" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Test 1: Check if backend can start
Write-Host "1. Testing Backend Startup..." -ForegroundColor Yellow
try {
    cd backend
    $backendProcess = Start-Process python -ArgumentList "app.py" -NoNewWindow -PassThru
    Start-Sleep 3
    if (!$backendProcess.HasExited) {
        Write-Host "✅ Backend started successfully" -ForegroundColor Green
        Stop-Process -Id $backendProcess.Id -Force
    } else {
        Write-Host "❌ Backend failed to start" -ForegroundColor Red
    }
    cd ..
} catch {
    Write-Host "❌ Backend test failed: $($_.Exception.Message)" -ForegroundColor Red
    cd ..
}

# Test 2: Check environment variables
Write-Host "2. Checking Environment Variables..." -ForegroundColor Yellow
$envFile = "backend\.env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile
    $firebaseConfigured = $envContent | Select-String "FIREBASE_PROJECT_ID" | Where-Object { $_.Line -notmatch "^#" }
    $supabaseConfigured = $envContent | Select-String "SUPABASE_URL" | Where-Object { $_.Line -notmatch "^#" }

    if ($firebaseConfigured) {
        Write-Host "✅ Firebase credentials configured" -ForegroundColor Green
    } else {
        Write-Host "❌ Firebase credentials missing" -ForegroundColor Red
    }

    if ($supabaseConfigured) {
        Write-Host "✅ Supabase credentials configured" -ForegroundColor Green
    } else {
        Write-Host "❌ Supabase credentials missing" -ForegroundColor Red
    }
} else {
    Write-Host "❌ .env file not found" -ForegroundColor Red
}

# Test 3: Check if database schema files exist
Write-Host "3. Checking Database Schema Files..." -ForegroundColor Yellow
$schemaFiles = @(
    "database\enhanced_schema.sql",
    "firebase_rls_policies.sql"
)

foreach ($file in $schemaFiles) {
    if (Test-Path $file) {
        Write-Host "✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing: $file" -ForegroundColor Red
    }
}

# Test 4: Check frontend configuration
Write-Host "4. Checking Frontend Configuration..." -ForegroundColor Yellow
$frontendFiles = @(
    "src\config\firebase.js",
    "src\config\supabase.js"
)

foreach ($file in $frontendFiles) {
    if (Test-Path $file) {
        Write-Host "✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing: $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Run the database schema in Supabase Dashboard" -ForegroundColor White
Write-Host "2. Apply the RLS policies" -ForegroundColor White
Write-Host "3. Test user registration through the app" -ForegroundColor White
Write-Host "4. Verify data is stored correctly" -ForegroundColor White
Write-Host ""
Write-Host "📚 Useful Commands:" -ForegroundColor Cyan
Write-Host "- Start backend: cd backend && python app.py" -ForegroundColor White
Write-Host "- Start frontend: npm start" -ForegroundColor White
Write-Host "- View Supabase: https://supabase.com/dashboard" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Integration test complete!" -ForegroundColor Green</content>
<parameter name="filePath">c:\Users\abayo\OneDrive\Desktop\thesis\medichain\test_integration.ps1
