# 📋 Pre-Deployment Checklist

Use this checklist before deploying to Render.com.

## Local Development Verification

### ✅ Code Quality
- [ ] All game features working locally
- [ ] No console errors in browser
- [ ] WebSocket connections stable
- [ ] Turn-based system working
- [ ] BINGO validation correct
- [ ] Auto-cleanup functioning

### ✅ Files Present
- [ ] `requirements.txt` updated
- [ ] `.env.example` created
- [ ] `build.sh` created
- [ ] `render.yaml` created
- [ ] `.gitignore` created
- [ ] `DEPLOYMENT.md` present
- [ ] `QUICK_START.md` present
- [ ] `README.md` updated

### ✅ Settings Configuration
- [ ] `settings.py` imports `os`, `decouple`, `dj_database_url`
- [ ] SECRET_KEY from environment
- [ ] DEBUG from environment
- [ ] ALLOWED_HOSTS from environment
- [ ] CSRF_TRUSTED_ORIGINS configured
- [ ] DATABASE_URL support added
- [ ] REDIS_URL support added
- [ ] WhiteNoise middleware present
- [ ] STATIC_ROOT configured
- [ ] Channel layers conditional (Redis/InMemory)

### ✅ Health Check
- [ ] `/health/` endpoint created in views.py
- [ ] URL pattern added in urls.py
- [ ] Returns JSON response

## Git Repository

### ✅ Commit All Changes
```bash
cd d:\Projects\Bingo\bingo_project
git status  # Check for uncommitted files
git add .
git commit -m "Add Render.com deployment configuration"
```

### ✅ Make build.sh Executable
```bash
git update-index --chmod=+x build.sh
git add build.sh
git commit -m "Make build.sh executable"
```

### ✅ Push to GitHub
```bash
git push origin main
# Or: git push origin master (depending on your branch)
```

### ✅ Verify on GitHub
- [ ] All files visible in repository
- [ ] Latest commit shows "deployment configuration"
- [ ] build.sh has executable permissions

## Render.com Setup

### ✅ Account Creation
- [ ] Render.com account created
- [ ] GitHub account connected
- [ ] Repository access granted

### ✅ Blueprint Deployment
- [ ] "New +" → "Blueprint" selected
- [ ] Correct repository chosen
- [ ] render.yaml detected
- [ ] Services created:
  - [ ] Web Service (bingo-game)
  - [ ] PostgreSQL (bingo-db)
  - [ ] Redis (bingo-redis)

### ✅ Environment Variables
Generate SECRET_KEY first:
```python
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Then configure:
- [ ] SECRET_KEY (generated value)
- [ ] DEBUG (set to `False`)
- [ ] ALLOWED_HOSTS (your-app-name.onrender.com)
- [ ] CSRF_TRUSTED_ORIGINS (https://your-app-name.onrender.com)
- [ ] DATABASE_URL (auto-set by Render)
- [ ] REDIS_URL (auto-set by Render)

### ✅ Initial Deployment
- [ ] "Manual Deploy" triggered
- [ ] Build logs show no errors
- [ ] "collectstatic" successful
- [ ] Migrations ran successfully
- [ ] Service shows "Live"

## Testing

### ✅ Basic Functionality
- [ ] App loads at Render URL
- [ ] Home page displays
- [ ] No 500 errors

### ✅ Room Creation
- [ ] Can create new room
- [ ] Room code generated
- [ ] Redirected to room page

### ✅ Room Joining
- [ ] Can join existing room
- [ ] Player name validation works
- [ ] Multiple players can join

### ✅ Board Setup
- [ ] "Generate Random Board" works
- [ ] "Clear Board" works
- [ ] Manual fill works (1-25)
- [ ] Board locked after game starts

### ✅ Ready System
- [ ] Ready button enables when board filled
- [ ] Player status shows colors correctly
- [ ] Start button enables when all ready
- [ ] Game starts for all players

### ✅ Gameplay
- [ ] Only current player can select
- [ ] Board locks/unlocks correctly
- [ ] Numbers cross out for all players
- [ ] Line counter updates
- [ ] Turn rotates automatically

### ✅ BINGO Validation
- [ ] BINGO button enables at 5 lines
- [ ] Winner announcement appears
- [ ] All players see winner
- [ ] Game ends properly

### ✅ Auto-Cleanup
- [ ] Room auto-deletes after winner (35s)
- [ ] Players redirected to home
- [ ] Room deleted on all disconnect

### ✅ WebSocket Connection
- [ ] Real-time updates work
- [ ] No WebSocket errors in console
- [ ] Connection stable during gameplay
- [ ] Reconnection works after disconnect

## Keep-Alive Setup

### ✅ Service Selection
Choose one:
- [ ] Option A: UptimeRobot (recommended)
- [ ] Option B: Cron-Job.org
- [ ] Option C: GitHub Actions

### ✅ UptimeRobot Configuration (If chosen)
- [ ] Account created at uptimerobot.com
- [ ] Monitor added
- [ ] Type: HTTP(s)
- [ ] URL: https://your-app-name.onrender.com/health/
- [ ] Interval: 5 minutes
- [ ] Monitor status: Active

### ✅ Verification
- [ ] Health endpoint returns 200 OK
- [ ] Response: `{"status": "ok", "message": "Bingo server is running"}`
- [ ] Monitor shows "Up"

## Post-Deployment

### ✅ Monitoring Setup
- [ ] UptimeRobot sending pings
- [ ] Render logs accessible
- [ ] No errors in Render logs

### ✅ Performance Check
- [ ] Response time < 1 second (after warmup)
- [ ] Cold start prevented by keep-alive
- [ ] WebSocket latency acceptable

### ✅ Security Verification
- [ ] DEBUG=False confirmed
- [ ] SECRET_KEY not in code
- [ ] .env not committed to Git
- [ ] HTTPS enforced

### ✅ Documentation
- [ ] README.md updated
- [ ] Deployment guides complete
- [ ] Environment variables documented

### ✅ Future Maintenance
- [ ] Calendar reminder for PostgreSQL expiration (90 days)
- [ ] Keep-alive service monitoring enabled
- [ ] Error notifications configured (Render)

## Final Checks

### ✅ Share & Test
- [ ] Share URL with friend
- [ ] Test from different devices
- [ ] Verify on mobile browser
- [ ] Check different network conditions

### ✅ Backup Plan
- [ ] Know how to view logs (Render dashboard)
- [ ] Know how to restart service
- [ ] Have deployment guides bookmarked
- [ ] Understand how to rollback if needed

## Common Issues Checklist

If deployment fails, check:
- [ ] build.sh is executable
- [ ] requirements.txt has all dependencies
- [ ] render.yaml syntax is correct
- [ ] Environment variables are set
- [ ] GitHub repository is up to date

If WebSocket fails, check:
- [ ] CSRF_TRUSTED_ORIGINS includes https://your-domain
- [ ] ALLOWED_HOSTS includes your-domain (no https://)
- [ ] Redis is running in Render dashboard
- [ ] Browser console for errors

If static files missing, check:
- [ ] WhiteNoise middleware added
- [ ] STATIC_ROOT configured
- [ ] collectstatic ran in build logs
- [ ] staticfiles/ folder created

## Success! 🎉

When all boxes checked:
- ✅ Your game is live
- ✅ Keep-alive is active
- ✅ Monitoring is setup
- ✅ Ready for players!

**Your URL:** https://your-app-name.onrender.com

Share it and enjoy! 🎮

---

**Need help?** See [DEPLOYMENT.md](DEPLOYMENT.md) for troubleshooting.
