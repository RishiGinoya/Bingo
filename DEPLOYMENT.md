# Deployment Guide - Render.com

This guide will help you deploy the Indian Bingo game to Render.com's free tier with keep-alive functionality.

## Prerequisites

- GitHub account
- Render.com account (free tier)
- Your code pushed to a GitHub repository

## Step 1: Prepare Your Repository

1. Ensure all files are committed to your GitHub repository:
   - `requirements.txt`
   - `.env.example`
   - `build.sh`
   - `render.yaml`
   - All project files

2. Make sure `build.sh` is executable (important):
   ```bash
   git add build.sh
   git update-index --chmod=+x build.sh
   git commit -m "Make build.sh executable"
   git push
   ```

## Step 2: Set Up Render.com

### A. Create Render Account
1. Go to [https://render.com](https://render.com)
2. Sign up using your GitHub account
3. Authorize Render to access your repositories

### B. Deploy from render.yaml
1. Go to your Render dashboard
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Select the repository containing your Bingo project
5. Render will automatically detect `render.yaml` and create:
   - Web Service (Bingo app)
   - PostgreSQL Database
   - Redis instance

### C. Configure Environment Variables
After deployment is created, go to your Web Service and add these environment variables:

```
SECRET_KEY=your-secret-key-here-generate-a-random-string
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
DATABASE_URL=(automatically set by Render)
REDIS_URL=(automatically set by Render)
```

**To generate a SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(50))
```

Replace `your-app-name` with the actual name you choose for your Render service.

## Step 3: Initial Deployment

1. After configuring environment variables, click **"Manual Deploy"** → **"Deploy latest commit"**
2. Wait for the build to complete (5-10 minutes)
3. Check the logs for any errors
4. Once deployed, click the URL to access your app

## Step 4: Set Up Keep-Alive Service

Since Render free tier spins down after 15 minutes of inactivity, we'll use a free ping service to keep it alive.

### Option A: UptimeRobot (Recommended - Easiest)

1. Go to [https://uptimerobot.com](https://uptimerobot.com)
2. Sign up for a free account
3. Click **"Add New Monitor"**
4. Configure:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** Bingo Game
   - **URL:** `https://your-app-name.onrender.com/`
   - **Monitoring Interval:** 5 minutes (free tier)
5. Click **"Create Monitor"**

UptimeRobot will ping your app every 5 minutes, keeping it awake.

### Option B: Cron-Job.org (Alternative)

1. Go to [https://cron-job.org](https://cron-job.org)
2. Sign up for a free account
3. Create a new cron job:
   - **Title:** Bingo Keep-Alive
   - **URL:** `https://your-app-name.onrender.com/`
   - **Schedule:** Every 14 minutes
4. Save and enable the cron job

### Option C: GitHub Actions (Developer-Friendly)

Create `.github/workflows/keep-alive.yml` in your repository:

```yaml
name: Keep Alive

on:
  schedule:
    - cron: '*/14 * * * *'  # Every 14 minutes
  workflow_dispatch:  # Allow manual trigger

jobs:
  keep-alive:
    runs-on: ubuntu-latest
    steps:
      - name: Ping the app
        run: |
          curl -I https://your-app-name.onrender.com/
```

Note: GitHub Actions may have usage limits on the free tier.

## Step 5: Database Migrations

The first deployment automatically runs migrations via `build.sh`. For future updates:

1. Push your code changes to GitHub
2. Render will automatically rebuild and deploy
3. Migrations run automatically during build

## Step 6: Testing

1. Visit your Render URL: `https://your-app-name.onrender.com`
2. Create a new game room
3. Open the room in two different browsers/tabs
4. Test the gameplay:
   - Generate random boards
   - Mark players ready
   - Take turns selecting numbers
   - Verify BINGO validation works
   - Check auto-cleanup after game ends

## Troubleshooting

### Cold Start Issues
- **Symptom:** First request takes 30+ seconds
- **Solution:** This is normal on free tier. Keep-alive service prevents this.

### WebSocket Connection Fails
- **Check:** CSRF_TRUSTED_ORIGINS includes your Render URL
- **Check:** ALLOWED_HOSTS includes your Render domain
- **Check:** Redis is running (check Render dashboard)

### Static Files Not Loading
- **Run:** Manual deployment to trigger `collectstatic`
- **Check:** Build logs show "X static files copied to '/opt/render/project/src/staticfiles'"

### Database Connection Errors
- **Check:** DATABASE_URL environment variable is set
- **Check:** PostgreSQL database is running in Render dashboard
- **Solution:** Render automatically sets this when using Blueprint

### Redis Connection Errors
- **Check:** REDIS_URL environment variable is set
- **Check:** Redis instance is running in Render dashboard

### Application Logs
View logs in Render dashboard:
1. Go to your Web Service
2. Click **"Logs"** tab
3. Check for errors

## Monitoring

### Check Service Status
- Render Dashboard shows service health
- UptimeRobot/Cron-Job.org shows ping history

### View Active Connections
- Check Render logs for WebSocket connections
- Look for "Player X connected" messages

### Performance
- Free tier has limited resources
- Expect ~2-4 concurrent users max
- For more users, upgrade to paid tier ($7/month)

## Updating Your App

1. Make code changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```
3. Render auto-deploys on push (if enabled)
4. Or manually deploy from Render dashboard

## Cost Information

- **Web Service:** Free (750 hours/month with limitations)
- **PostgreSQL:** Free (expires after 90 days, migrate data)
- **Redis:** Free (25 MB storage)
- **Keep-Alive Service:** Free (UptimeRobot or Cron-Job.org)

**Note:** Free PostgreSQL databases expire after 90 days. You'll need to create a new one and migrate data.

## Security Best Practices

1. Never commit `.env` file with real credentials
2. Use strong SECRET_KEY (50+ characters)
3. Keep DEBUG=False in production
4. Regularly update dependencies
5. Monitor Render logs for suspicious activity

## Support

- Render Documentation: [https://render.com/docs](https://render.com/docs)
- Django Channels: [https://channels.readthedocs.io](https://channels.readthedocs.io)
- Project README: See `README.md` for game features

## Quick Commands

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Test local deployment setup
python manage.py check --deploy

# Make build.sh executable
git update-index --chmod=+x build.sh

# View PostgreSQL info (from Render dashboard)
# Go to Database → Connect → Copy connection string
```

## Next Steps

After successful deployment:
1. ✅ Set up keep-alive monitoring
2. ✅ Share your game URL with friends
3. ✅ Monitor performance and errors
4. ✅ Consider upgrading if you need more resources
5. ✅ Set calendar reminder for PostgreSQL expiration (90 days)

Happy gaming! 🎮
