# Deploy Ghost User (100% Free)

## Option 1: Fly.io (Recommended — can run Playwright)

1. Install Fly CLI:
   ```bash
   curl -fsSL https://fly.io/install.sh | sh
   ```
2. Sign up: `fly auth signup` (free tier, no credit card)
3. Deploy:
   ```bash
   fly launch --no-deploy
   fly secrets set JWT_SECRET=<random-string>
   fly secrets set GEMINI_API_KEY=<your-key>
   fly deploy
   ```

Your app will be at `https://ghost-user.fly.dev`

## Option 2: Render.com (Free, no Playwright — use Browserless)

1. Push code to GitHub
2. Go to https://render.com → New Web Service
3. Connect repo, set:
   - Build: `pip install -r requirements.txt && python -m playwright install chromium`
   - Start: `cd backend && uvicorn main:app --host 0.0.0.0 --port 10000`
4. Add environment variables
5. For Playwright, add a Browserless.io free account in code

## Required env vars on deploy

```
JWT_SECRET=<random-string>
GEMINI_API_KEY=<your-key>
LLM_PROVIDER=gemini
```

## Free Resources Summary

| Service | What it gives | Limits |
|---------|--------------|--------|
| Fly.io | 3 VMs, Docker, Playwright | 256MB RAM each, sleeps on idle |
| Supabase | PostgreSQL, Auth, Storage | 500MB DB, 1GB storage |
| Resend | Email sending | 100 emails/day |
| Cloudflare | Domain, SSL, CDN | Free tier |
| Google Gemini | LLM analysis | 60 req/min free |
