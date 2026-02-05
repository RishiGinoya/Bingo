# Render.com Deployment - Quick Start Guide

## 🚀 Quick Overview

Your Indian Bingo game is ready to deploy to Render.com's free tier! This setup includes:
- ✅ WebSocket support for real-time multiplayer
- ✅ PostgreSQL database
- ✅ Redis for Django Channels
- ✅ Keep-alive mechanism to prevent cold starts
- ✅ Static files serving with WhiteNoise

## 📋 Pre-Deployment Checklist

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Make build.sh executable**
   ```bash
   git update-index --chmod=+x build.sh
   git add build.sh
   git commit -m "Make build.sh executable"
   git push
   ```

## 🔧 Files Created for Deployment

### 1. `.env.example` - Template for environment variables
Located in project root. Copy this for local development.

### 2. `build.sh` - Render build script
Automatically installs dependencies and runs migrations.

### 3. `render.yaml` - Infrastructure configuration
Defines web service, PostgreSQL, and Redis setup.

### 4. `settings.py` - Updated for production
- Environment variable support via `python-decouple`
- PostgreSQL database configuration
- Redis channel layers
- WhiteNoise for static files
- CSRF trusted origins

### 5. `requirements.txt` - Updated dependencies
```
Django>=5.2.0
channels>=4.0.0
daphne>=4.0.0
channels-redis>=4.0.0
asgiref>=3.7.0
psycopg2-binary>=2.9.9
python-decouple>=3.8
gunicorn>=21.2.0
whitenoise>=6.6.0
```

### 6. Health Check Endpoint
Added `/health/` endpoint for keep-alive monitoring.

## 🌐 Deployment Steps

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 2: Deploy with Blueprint
1. Click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository
3. Render detects `render.yaml` automatically
4. Creates: Web Service + PostgreSQL + Redis

### Step 3: Configure Environment Variables
In your Web Service settings, add:

```bash
# Generate SECRET_KEY first:
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Then set:
```
SECRET_KEY=<generated-key-here>
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
```

(DATABASE_URL and REDIS_URL are auto-set by Render)

### Step 4: Deploy
Click **"Manual Deploy"** → **"Deploy latest commit"**

Wait 5-10 minutes for first deployment.

### Step 5: Set Up Keep-Alive

#### Option A: UptimeRobot (Recommended)
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Add New Monitor:
   - Type: HTTP(s)
   - URL: `https://your-app-name.onrender.com/health/`
   - Interval: 5 minutes
3. Done! ✅

#### Option B: Cron-Job.org
1. Go to [cron-job.org](https://cron-job.org)
2. Create cron job:
   - URL: `https://your-app-name.onrender.com/health/`
   - Schedule: Every 14 minutes

#### Option C: GitHub Actions
Create `.github/workflows/keep-alive.yml`:

```yaml
name: Keep Alive
on:
  schedule:
    - cron: '*/14 * * * *'
  workflow_dispatch:

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - run: curl -I https://your-app-name.onrender.com/health/
```

## 🎮 Testing Your Deployment

1. Visit: `https://your-app-name.onrender.com`
2. Create a room
3. Open in 2 browser tabs/windows
4. Test gameplay:
   - ✅ Generate boards
   - ✅ Mark ready
   - ✅ Turn-based selection
   - ✅ BINGO validation
   - ✅ Auto-cleanup

## 🐛 Troubleshooting

### Cold Start (30+ seconds)
**Normal on free tier.** Keep-alive prevents this.

### WebSocket Errors
Check:
- CSRF_TRUSTED_ORIGINS set correctly
- ALLOWED_HOSTS includes your domain
- Redis is running (Render dashboard)

### Static Files Missing
- Check build logs for "collectstatic" success
- Verify STATIC_ROOT in settings.py

### Database Errors
- Verify DATABASE_URL is set
- Check PostgreSQL status in dashboard

## 💰 Cost Breakdown

- **Web Service:** Free (750 hrs/month)
- **PostgreSQL:** Free (expires in 90 days)
- **Redis:** Free (25 MB)
- **Keep-Alive:** Free

**Note:** PostgreSQL free tier expires after 90 days. Plan to migrate data.

## 📊 Monitoring

- **Render Dashboard:** Service health, logs
- **UptimeRobot:** Uptime history
- **Logs:** Click "Logs" tab in Render

## 🔄 Updating Your App

```bash
git add .
git commit -m "Update"
git push
```

Render auto-deploys (if enabled) or manually trigger from dashboard.

## 🔒 Security Notes

- Never commit `.env` with real secrets
- Use 50+ character SECRET_KEY
- Keep DEBUG=False in production
- Monitor logs regularly

## 📚 Additional Resources

- Full Guide: See `DEPLOYMENT.md`
- Game Features: See `README.md`
- Render Docs: [render.com/docs](https://render.com/docs)

## ✅ Post-Deployment

1. Set up keep-alive (UptimeRobot/Cron-Job.org)
2. Test all game features
3. Share your URL!
4. Monitor performance
5. Calendar reminder for DB expiration (90 days)

## 🆘 Need Help?

Check these in order:
1. Render logs (Dashboard → Logs)
2. `DEPLOYMENT.md` (detailed troubleshooting)
3. Render documentation
4. Django Channels docs

---

**Your app URL will be:** `https://your-app-name.onrender.com`

Happy gaming! 🎉
