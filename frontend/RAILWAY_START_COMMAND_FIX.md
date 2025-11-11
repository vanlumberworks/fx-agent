# Railway Start Command Fix

## Problem

Railway deployment succeeds but crashes immediately with:
```
npm error No workspaces found:
npm error   --workspace=forex-agent-frontend
```

This means Railway is trying to run `npm run dev --workspace=forex-agent-frontend` which is incorrect for the frontend-only deployment.

---

## Root Cause

Railway is **not using the `nixpacks.toml` start command**. Instead, it's using:
- A cached/detected start command from the monorepo root
- OR a custom start command configured in Railway settings
- OR Root Directory is not set to `frontend/`

---

## Solution 1: Set Custom Start Command (RECOMMENDED)

### Steps:

1. **Open Railway Dashboard** → https://railway.app
2. **Select your frontend service**
3. **Click "Settings" tab**
4. **Scroll to "Deploy" section**
5. **Find "Start Command" or "Custom Start Command"**
6. **Enter this command**:
   ```bash
   pnpm preview --host 0.0.0.0 --port $PORT
   ```
7. **Click "Save" or "Update"**
8. **Go to "Deployments" tab**
9. **Click "Redeploy"** (or push a new commit)

### Screenshot Guide:
```
Railway Dashboard
├── Your Project
│   └── Frontend Service
│       └── Settings ⬅️ Click here
│           ├── General
│           ├── Service
│           │   └── Root Directory: frontend ⬅️ Verify this is set
│           └── Deploy
│               └── Start Command: [pnpm preview --host 0.0.0.0 --port $PORT] ⬅️ Set this
```

---

## Solution 2: Verify Root Directory + Clear Start Command

If you want Railway to use `nixpacks.toml` automatically:

### Steps:

1. **Railway Dashboard** → Your service → **Settings**
2. **Verify "Root Directory"** is set to: `frontend`
3. **Find "Start Command"** field
4. **If it's filled**, clear it (leave empty)
5. **Save and Redeploy**

When Start Command is empty, Railway uses the command from `nixpacks.toml`:
```toml
[start]
cmd = "pnpm preview --host 0.0.0.0 --port $PORT"
```

---

## Solution 3: Use Dockerfile Instead

If nixpacks continues to cause issues, Railway can use the `Dockerfile`:

### Steps:

1. **Railway Dashboard** → Settings → **Deploy** section
2. **Find "Builder"** or **"Build Configuration"**
3. **Select "Dockerfile"** (if available)
4. **Dockerfile path**: `frontend/Dockerfile`
5. **Save and Redeploy**

The Dockerfile has the correct start command at the end:
```dockerfile
CMD ["sh", "-c", "pnpm vite preview --host 0.0.0.0 --port ${PORT:-3000}"]
```

---

## Verification

After redeploying with the correct start command, Railway logs should show:

✅ **Good Logs:**
```
> forex-agent-frontend@1.0.0 preview
> vite preview --host 0.0.0.0 --port 3000

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://0.0.0.0:3000/
  ➜  press h to show help
```

❌ **Bad Logs:**
```
npm error No workspaces found:
npm error   --workspace=forex-agent-frontend
```

---

## Troubleshooting

### Issue: "pnpm: command not found"

**Cause**: Railway not detecting pnpm

**Solution**: Use the Dockerfile approach (Solution 3) instead of nixpacks

---

### Issue: "Cannot find module 'vite'"

**Cause**: Start command running in wrong directory or deps not installed

**Solution**:
1. Verify Root Directory is `frontend`
2. Check build logs show `pnpm install` succeeded
3. Try full path: `cd /app && pnpm preview --host 0.0.0.0 --port $PORT`

---

### Issue: Port binding error

**Error**: `EADDRINUSE: address already in use :::3000`

**Solution**: Railway sets the `$PORT` variable automatically. Ensure command uses `$PORT`:
```bash
pnpm preview --host 0.0.0.0 --port $PORT
```

NOT a hardcoded port:
```bash
pnpm preview --host 0.0.0.0 --port 3000  ❌
```

---

### Issue: Still seeing npm workspace errors after fix

**Cause**: Railway using cached deployment

**Solution**:
1. **Clear build cache**: Settings → "Delete Build Cache"
2. **Force rebuild**: Deployments → "Redeploy"
3. **OR push a dummy commit**:
   ```bash
   git commit --allow-empty -m "Trigger Railway rebuild"
   git push
   ```

---

## Why This Happened

Your monorepo has this structure:
```
fx-agent/
├── package.json          # Root package.json with workspaces
│   └── workspaces: ["frontend"]
├── frontend/
│   ├── package.json      # Frontend package
│   ├── nixpacks.toml     # Railway config
│   └── Dockerfile        # Alternative Railway config
└── backend/              # Python backend
```

Railway **detected the root `package.json`** which has:
```json
{
  "workspaces": ["frontend"]
}
```

And tried to run:
```bash
npm run dev --workspace=forex-agent-frontend
```

But since Root Directory is `frontend/`, Railway is inside the frontend directory where:
- ❌ There's no workspace configuration
- ❌ npm is not installed (should use pnpm)
- ✅ `nixpacks.toml` has correct command (but Railway ignoring it)

---

## Recommended Configuration

For Railway frontend deployment:

| Setting | Value |
|---------|-------|
| **Root Directory** | `frontend` |
| **Start Command** | `pnpm preview --host 0.0.0.0 --port $PORT` |
| **Build Command** | `pnpm install && pnpm build` (auto-detected) |
| **Environment Variable** | `VITE_API_URL=https://fx-agent-prod-thrumming-smoke-7736.fly.dev` |

---

## Testing Locally

To verify the start command works:

```bash
cd frontend
pnpm build
pnpm preview --host 0.0.0.0 --port 3000
```

Then open: http://localhost:3000

You should see the frontend running.

---

## Production Note

⚠️ **Important**: `vite preview` is NOT recommended for production by Vite team.

For production, consider:

### Option 1: Using `serve` package
```bash
# In Railway Start Command:
pnpm dlx serve -s dist -l $PORT
```

### Option 2: Using a proper Node server
Create `server.js` and use Express/Fastify to serve static files.

### Option 3: Deploy to static hosting
Use Vercel/Netlify/Cloudflare Pages for frontend, Railway for backend only.

See `RAILWAY_DEPLOYMENT.md` for more production deployment options.

---

## Quick Reference

**The correct start command for Railway:**
```bash
pnpm preview --host 0.0.0.0 --port $PORT
```

**Where to set it:**
Railway Dashboard → Service → Settings → Deploy → Start Command

**Don't forget:**
- Root Directory: `frontend`
- Environment Variables: `VITE_API_URL`

---

## Next Steps

After fixing the start command and redeploying:

1. ✅ Verify deployment doesn't crash
2. ✅ Check Railway logs show vite preview starting
3. ✅ Open Railway-provided URL
4. ✅ Test frontend loads
5. ✅ Add `VITE_API_URL` environment variable
6. ✅ Update backend CORS with Railway domain
7. ✅ Test full analysis workflow

---

## Support

- Railway Docs: https://docs.railway.app/
- Vite Preview: https://vitejs.dev/guide/cli.html#vite-preview
- This project: See `RAILWAY_SETUP_QUICK_START.md`
