# Quick Deploy Script

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "    CARBONSENSE AI - DEPLOYMENT ASSISTANT" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "Git is not installed!" -ForegroundColor Red
    Write-Host "   Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}
Write-Host "Git is installed" -ForegroundColor Green

# Initialize git if needed
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "Git initialized" -ForegroundColor Green
}
else {
    Write-Host "Git repository already exists" -ForegroundColor Green
}

# Stage all files
Write-Host ""
Write-Host "Staging files for deployment..." -ForegroundColor Yellow
git add .
Write-Host "Files staged" -ForegroundColor Green

# Show status
Write-Host ""
Write-Host "Repository Status:" -ForegroundColor Cyan
git status --short

# Offer to commit
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT OPTIONS:" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Deploy to Render.com (RECOMMENDED - 100% Free)" -ForegroundColor Green
Write-Host "   - No credit card required"
Write-Host "   - Automatic HTTPS"
Write-Host "   - Custom domain support"
Write-Host ""
Write-Host "2. Deploy to Railway.app (Dollar 5 free credit/month)" -ForegroundColor Yellow
Write-Host "   - Easy CLI deployment"
Write-Host "   - Fast deployment"
Write-Host ""
Write-Host "3. Deploy to Fly.io (3 free VMs)" -ForegroundColor Cyan
Write-Host "   - Global edge deployment"
Write-Host "   - CLI-based"
Write-Host ""
Write-Host "4. Manual GitHub Push" -ForegroundColor White
Write-Host "   - I will push to GitHub manually"
Write-Host ""

$choice = Read-Host "Select deployment option (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "RENDER.COM DEPLOYMENT" -ForegroundColor Green
        Write-Host "=======================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Your project is already configured for Render!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Yellow
        Write-Host "1. Create GitHub repository at: https://github.com/new" -ForegroundColor White
        Write-Host "2. Run these commands to push:" -ForegroundColor White
        Write-Host ""
        Write-Host '   git commit -m "Deploy CarbonSense AI"' -ForegroundColor Cyan
        Write-Host '   git remote add origin https://github.com/YOUR_USERNAME/carbonsense-ai.git' -ForegroundColor Cyan
        Write-Host '   git branch -M main' -ForegroundColor Cyan
        Write-Host '   git push -u origin main' -ForegroundColor Cyan
        Write-Host ""
        Write-Host "3. Go to: https://render.com" -ForegroundColor White
        Write-Host "4. Sign up with GitHub" -ForegroundColor White
        Write-Host "5. Click 'New +' then 'Web Service'" -ForegroundColor White
        Write-Host "6. Select your repository" -ForegroundColor White
        Write-Host "7. Click 'Create Web Service'" -ForegroundColor White
        Write-Host ""
        Write-Host "Your app will be live at: https://carbonsense-ai.onrender.com" -ForegroundColor Green
    }
    "2" {
        Write-Host ""
        Write-Host "RAILWAY.APP DEPLOYMENT" -ForegroundColor Yellow
        Write-Host "=======================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Yellow
        Write-Host "1. Install Railway CLI:" -ForegroundColor White
        Write-Host '   npm install -g @railway/cli' -ForegroundColor Cyan
        Write-Host ""
        Write-Host "2. Deploy:" -ForegroundColor White
        Write-Host '   railway login' -ForegroundColor Cyan
        Write-Host '   railway init' -ForegroundColor Cyan
        Write-Host '   railway up' -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Your app will be live at: https://your-app.railway.app" -ForegroundColor Green
    }
    "3" {
        Write-Host ""
        Write-Host "FLY.IO DEPLOYMENT" -ForegroundColor Cyan
        Write-Host "=======================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Yellow
        Write-Host "1. Install Fly CLI:" -ForegroundColor White
        Write-Host '   powershell -Command "irm https://fly.io/install.ps1 | iex"' -ForegroundColor Cyan
        Write-Host ""
        Write-Host "2. Deploy:" -ForegroundColor White
        Write-Host '   fly launch' -ForegroundColor Cyan
        Write-Host '   fly deploy' -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Your app will be live at: https://carbonsense-ai.fly.dev" -ForegroundColor Green
    }
    "4" {
        Write-Host ""
        Write-Host "MANUAL GITHUB PUSH" -ForegroundColor White
        Write-Host "=======================================================" -ForegroundColor Cyan
        Write-Host ""
        
        $commitMsg = Read-Host "Enter commit message (or press Enter for default)"
        if ([string]::IsNullOrWhiteSpace($commitMsg)) {
            $commitMsg = "Deploy CarbonSense AI"
        }
        
        git commit -m $commitMsg
        
        Write-Host ""
        Write-Host "Changes committed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Yellow
        Write-Host "1. Create GitHub repository at: https://github.com/new" -ForegroundColor White
        Write-Host "2. Run:" -ForegroundColor White
        Write-Host '   git remote add origin https://github.com/YOUR_USERNAME/carbonsense-ai.git' -ForegroundColor Cyan
        Write-Host '   git branch -M main' -ForegroundColor Cyan
        Write-Host '   git push -u origin main' -ForegroundColor Cyan
    }
    default {
        Write-Host ""
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "For detailed instructions, see: DEPLOYMENT_GUIDE.md" -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
