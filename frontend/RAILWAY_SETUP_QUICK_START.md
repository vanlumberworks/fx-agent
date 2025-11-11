# Railway Frontend Deployment - Quick Start

## The Problem

Railway is using the **root Python Dockerfile** instead of building your frontend. You're seeing:
```
Using Detected Dockerfile
FROM docker.io/library/python:3.12-slim
```

## Two Solutions (Choose One)

---

### ✅ Solution 1: Configure Root Directory (RECOMMENDED)

This uses the `nixpacks.toml` configuration I created.

#### Steps:

1. **Open Railway Dashboard** → https://railway.app
2. **Select your project** and **click your service**
3. **Click "Settings" tab** (top navigation)
4. **Find "Service" or "Build" section**
5. **Look for "Root Directory"** field
6. **Enter**: `frontend`
7. **Scroll down and click "Save"** (if there's a save button)
8. **Go back to "Deployments" tab**
9. **Click "Deploy"** or push a new commit

#### What this does:
- Tells Railway to look in `frontend/` directory
- Uses `nixpacks.toml` (Node.js 20 + pnpm)
- Ignores the root Python Dockerfile

#### Visual Guide:
```
Railway Dashboard
├── Your Project
│   └── Your Service
│       └── Settings ⬅️ Click here
│           ├── General
│           ├── Service
│           │   └── Root Directory: [frontend] ⬅️ Enter this
│           └── Build
```

---

### ✅ Solution 2: Use Frontend Dockerfile (ALTERNATIVE)

If you can't find the Root Directory setting, use the Dockerfile I created in `frontend/Dockerfile`.

#### Steps:

1. **Commit and push** the new files:
   ```bash
   git add frontend/Dockerfile frontend/nixpacks.toml frontend/.railwayignore
   git commit -m "Add frontend Dockerfile for Railway"
   git push
   ```

2. **In Railway Dashboard**:
   - **Still set Root Directory to `frontend`** if possible
   - OR Railway will auto-detect `frontend/Dockerfile`

3. **Railway will now**:
   - Use the frontend Dockerfile
   - Build with Node.js 20 + pnpm
   - Create production image

#### What's in the Dockerfile:
- Multi-stage build (smaller image)
- Node.js 20 Alpine
- pnpm package manager
- Vite build + preview server
- Port configuration for Railway

---

## How to Set Root Directory in Railway

Railway's UI can vary, but here are the most common locations:

### Option A: New Railway UI (2024+)
1. Project → Service → **Settings**
2. Look for **"Service Settings"** section
3. Find **"Root Directory"** or **"Source Directory"**
4. Enter: `frontend`
5. Save changes

### Option B: Old Railway UI
1. Service → **Settings**
2. Scroll to **"Build"** section
3. Find **"Root Directory"**
4. Enter: `frontend`
5. Changes auto-save

### Option C: Via railway.json (Alternative)

If you still can't find it, create `railway.json` in your **project root**:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd frontend && pnpm install && pnpm build",
    "watchPatterns": ["frontend/**"]
  },
  "deploy": {
    "startCommand": "cd frontend && pnpm preview --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Then commit and push:
```bash
git add railway.json
git commit -m "Add Railway configuration"
git push
```

---

## Verification

After configuring, your Railway build logs should show:

✅ **GOOD** (Using nixpacks or frontend Dockerfile):
```
=========================
Using Nixpacks
=========================
installing nodejs_20, pnpm
```

OR

```
=========================
Using Detected Dockerfile
=========================
FROM node:20-alpine
```

❌ **BAD** (Still using root Dockerfile):
```
FROM docker.io/library/python:3.12-slim
```

---

## Troubleshooting

### Railway still uses Python Dockerfile

**Solution**:
1. Make sure you **committed and pushed** all new files
2. **Clear build cache**: Settings → "Clear Build Cache"
3. **Force redeploy**: Deployments → "Redeploy"
4. **Double-check** Root Directory is set to `frontend`

### "pnpm: command not found"

**Solution**:
- If using nixpacks: Check `nixpacks.toml` exists in `frontend/`
- If using Dockerfile: Check `frontend/Dockerfile` has `corepack enable`

### Build succeeds but app crashes

**Solution**:
Check start command includes `--host 0.0.0.0 --port $PORT`

```bash
pnpm preview --host 0.0.0.0 --port $PORT
```

### Can't find Root Directory setting

**Solutions**:
1. Use `railway.json` approach (see Option C above)
2. Use `frontend/Dockerfile` approach (Solution 2)
3. Contact Railway support or check their docs: https://docs.railway.app/

---

## Next Steps After Successful Deploy

1. ✅ Test the deployed URL
2. ✅ Check browser console for errors
3. ✅ Verify all routes work (client-side routing)
4. ✅ Add environment variables if needed (Settings → Variables)
5. ✅ Set up custom domain (Settings → Networking)
6. ✅ Consider switching from `vite preview` to a production server

---

## Quick Commands Reference

```bash
# Push changes
git add .
git commit -m "Configure Railway deployment"
git push

# Test build locally
cd frontend
pnpm install
pnpm build
pnpm preview  # Should work on localhost

# Check if Railway detects correctly
# (After setting Root Directory to 'frontend')
# Build logs should show Node.js/pnpm, NOT Python
```

---

## Support

- Railway Docs: https://docs.railway.app/guides/dockerfiles
- Railway Discord: https://discord.gg/railway
- This project's detailed guide: `RAILWAY_DEPLOYMENT.md`

---

## TL;DR

**Easiest fix**:
1. Railway Dashboard → Your Service → Settings
2. Set "Root Directory" to `frontend`
3. Redeploy

**If that doesn't work**:
1. Push the `frontend/Dockerfile` I created
2. Make sure Root Directory is still `frontend`
3. Redeploy
