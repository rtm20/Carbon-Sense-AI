# CarbonSense AI - Free Deployment Guide

## 🚀 Deploy to Render.com (100% Free)

### **What You Get:**
- ✅ Free hosting forever
- ✅ Automatic HTTPS
- ✅ Custom domain support
- ✅ Auto-deploy from GitHub
- ✅ No credit card required

---

## 📋 **Deployment Steps**

### **1. Prepare Your Repository**

Your project is already configured with:
- ✅ `render.yaml` - Render configuration
- ✅ `Procfile` - Start command
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - Updated with gunicorn

### **2. Push to GitHub**

```bash
cd "C:\Learning\Carbon Sense AI\carbonsense-demo"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Deploy CarbonSense AI"

# Create GitHub repo at https://github.com/new
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/carbonsense-ai.git
git branch -M main
git push -u origin main
```

### **3. Deploy on Render**

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with GitHub
4. Click **"New +"** → **"Web Service"**
5. Connect your `carbonsense-ai` repository
6. Render auto-detects `render.yaml` - click **"Apply"**
7. Click **"Create Web Service"**

**Done!** Your app will be live at: `https://carbonsense-ai.onrender.com`

---

## 🌐 **Alternative Free Options**

### **Option 2: Railway.app**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Live at**: `https://your-app.railway.app`  
**Free**: $5 credit/month

---

### **Option 3: Fly.io**

```bash
# Install Fly CLI
powershell -Command "irm https://fly.io/install.ps1 | iex"

# Deploy
fly launch
fly deploy
```

**Live at**: `https://carbonsense-ai.fly.dev`  
**Free**: 3 small VMs

---

### **Option 4: PythonAnywhere**

1. Go to **https://www.pythonanywhere.com**
2. Sign up for free account
3. Upload your code via **Files** tab
4. Configure web app in **Web** tab
5. Set WSGI file to point to `backend/app.py`

**Live at**: `https://yourusername.pythonanywhere.com`

---

## 🎯 **Comparison**

| Platform | Free Tier | HTTPS | Custom Domain | Best For |
|----------|-----------|-------|---------------|----------|
| **Render** | ✅ Forever | ✅ Yes | ✅ Yes | **Flask apps** |
| **Railway** | $5/month credit | ✅ Yes | ✅ Yes | Quick deploys |
| **Fly.io** | 3 VMs free | ✅ Yes | ✅ Yes | Global edge |
| **PythonAnywhere** | Limited CPU | ❌ HTTP only | ✅ Yes | Simple Python |

---

## 🔧 **Configuration Notes**

### **Environment Variables (if needed)**

On Render dashboard:
- Go to **Environment** tab
- Add variables like:
  - `PYTHON_ENV=production`
  - `PORT=10000` (auto-set by Render)

### **Database (if needed later)**

Render provides free PostgreSQL:
- Click **"New +"** → **"PostgreSQL"**
- Free tier: 90 days, then $7/month

---

## ⚡ **What Happens on Deploy**

1. **Build Phase**: 
   - Installs Python 3.12
   - Runs `pip install -r requirements.txt`
   - Trains AI models (first time only)

2. **Start Phase**:
   - Runs `gunicorn backend.app:app`
   - Binds to `$PORT` (provided by platform)
   - Starts Flask server

3. **Live**:
   - Your API at `https://your-app.com/api/*`
   - Frontend at `https://your-app.com/frontend/`
   - Dashboard at `https://your-app.com/frontend/index.html`

---

## 📱 **Accessing Your Deployed App**

Once deployed, users can access:

- **Main Dashboard**: `https://your-app.com/frontend/index.html`
- **Model Performance**: `https://your-app.com/frontend/model_performance.html`
- **API Endpoint**: `https://your-app.com/api/optimize`

---

## 🐛 **Troubleshooting**

### **Build Fails**
- Check `requirements.txt` has correct versions
- View logs in Render dashboard

### **App Crashes on Start**
- Check if models are loading correctly
- Add error handling in `backend/app.py`

### **Slow Response**
- Free tier has cold starts (~30 seconds)
- Upgrade to paid tier ($7/month) for always-on

---

## 🎉 **Next Steps**

1. **Deploy to Render** (recommended)
2. **Share your URL** with users
3. **Monitor logs** in Render dashboard
4. **Add custom domain** (optional, free)
5. **Set up auto-deploy** from GitHub

---

## 💡 **Pro Tips**

- Free tier sleeps after 15 min inactivity
- First request takes ~30 seconds (cold start)
- Keep app alive with: https://uptimerobot.com (free pings)
- Enable auto-deploy: pushes to `main` auto-update

---

**Your CarbonSense AI is ready to share with the world! 🌍**
