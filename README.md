# AI Image Object Remover
**By Nova Technologies** · Web · AI · Hosting · Marketing · Apps
Contact: novamarketingdon@gmail.com
Built: March 2026

---

## What It Does

A free, browser-based AI tool that removes watermarks, logos, text, buttons, and any unwanted object from images using **OpenCV TELEA inpainting** — the same algorithm used in professional photo restoration software.

**No API costs. Runs 100% on your VPS. No sign-up. No limits.**

### How It Works (User Flow)
1. User uploads an image (JPEG, PNG, WebP — max 20MB)
2. User paints over the object/watermark with a red brush
3. Flask backend receives image + mask → OpenCV inpaints the masked area
4. User gets before/after comparison + download link
5. All files auto-deleted after **20 minutes**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.x, Gunicorn |
| Image Processing | OpenCV TELEA (`cv2.inpaint`), Pillow, NumPy |
| Scheduler | APScheduler (cleanup every 5 min) |
| Frontend | Vanilla HTML/CSS/JS — no frameworks |
| Fonts | Ubuntu (Google Fonts) |
| Deployment | Docker → Coolify → Contabo VPS |
| Ads | Google AdSense (slots pre-placed) |

**No external AI API required.** Processing is local OpenCV — $0 per image.

---

## Project Structure

```
image-object-remover/
├── app.py                      # Flask app — all routes + inpainting logic
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker build config for Coolify
├── .dockerignore
├── .env                        # Local env vars (empty — no API keys needed)
├── .gitignore
├── start.sh                    # Local dev startup script
├── uploads/                    # Temp image storage (auto-cleaned every 5 min)
├── static/
│   └── style.css               # Nova Technologies dark theme
└── templates/
    ├── base.html               # Shared layout: nav, AdSense script, footer
    ├── index.html              # Main tool (Step 1: Upload → Step 2: Paint → Step 3: Result)
    ├── about.html              # About page (required for AdSense)
    ├── privacy.html            # Privacy Policy (required for AdSense)
    ├── blog.html               # Blog index — 4 article cards
    ├── blog_watermark.html     # "How to Remove a Watermark" (SEO)
    ├── blog_logo.html          # "How to Remove a Logo" (SEO)
    ├── blog_text.html          # "How to Remove Text from Photo" (SEO)
    └── blog_inpainting.html    # "What Is AI Image Inpainting?" (SEO)
```

---

## Routes

| URL | Template | Purpose |
|---|---|---|
| `/` | `index.html` | Main tool |
| `/about` | `about.html` | About page |
| `/privacy` | `privacy.html` | Privacy Policy |
| `/blog` | `blog.html` | Blog index |
| `/blog/how-to-remove-watermark-from-image` | `blog_watermark.html` | SEO article |
| `/blog/remove-logo-from-image-online` | `blog_logo.html` | SEO article |
| `/blog/remove-text-from-photo-free` | `blog_text.html` | SEO article |
| `/blog/what-is-image-inpainting-ai` | `blog_inpainting.html` | SEO article |
| `POST /api/remove` | — | Inpainting endpoint |
| `/uploads/<filename>` | — | Serve processed images |

---

## Branding

| Property | Value |
|---|---|
| Business | Nova Technologies |
| Tagline | Web · AI · Hosting · Marketing · Apps |
| Brand email | novamarketingdon@gmail.com |
| Primary colour | `#0066FF` (blue) |
| Accent colour | `#FF6600` (orange) |
| Background | `#0a0f1e` (dark navy) |
| Font | Ubuntu (Google Fonts) |

---

## Local Development

```bash
cd /home/rouma/claude/tools/image-object-remover

# Create venv and install deps
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# Run dev server
venv/bin/python app.py
# → http://localhost:5000
```

Or use the startup script:
```bash
bash start.sh
```

---

## Deploy on Coolify (Contabo VPS — $8/month)

### VPS Specs
- **Plan:** Contabo VPS S
- **RAM:** 8 GB (app uses ~700 MB peak — 91% headroom)
- **Storage:** 50 GB SSD (app uses ~3 GB — 94% headroom)
- **CPU:** 4 vCPU (TELEA inpainting: 0.5–3s per image)
- **Capacity:** ~500–1,000 image removals/day with no performance issues

### Step 1 — Push to GitHub
```bash
cd /home/rouma/claude/tools/image-object-remover
git init
git add .
git commit -m "Initial deploy — AI Image Object Remover"
git remote add origin https://github.com/yourusername/image-object-remover.git
git push -u origin main
```

### Step 2 — Coolify Setup
1. Coolify UI → **New Resource → Application**
2. Source: **GitHub** → select repo
3. Build Pack: **Dockerfile**
4. Port: **`8000`**
5. Domain: your domain (e.g. `removeobject.co.ke`)
6. Enable **Auto Deploy** — deploys on every `git push`

### Step 3 — Environment Variables
No API keys required. Leave env vars empty in Coolify.
Coolify injects `PORT` automatically — the app reads it.

### Step 4 — Deploy
Click **Deploy**. Coolify builds the Docker image and starts the container.

### Future Updates
```bash
git add . && git commit -m "your message" && git push
# Coolify auto-deploys within ~60 seconds
```

---

## Docker Details

```dockerfile
# Base: python:3.12-slim
# System deps: libglib2.0-0, libsm6, libxext6, libxrender1, libgomp1 (for OpenCV)
# Workers: 2 Gunicorn workers
# Bind: 0.0.0.0:${PORT:-8000}
# Timeout: 120s (large images can take up to 30s to inpaint)
```

---

## Google AdSense Setup

### Pre-requisites Before Applying
- [ ] Site is live on a real domain (not localhost)
- [ ] `About` page exists at `/about` ✅
- [ ] `Privacy Policy` page exists at `/privacy` ✅
- [ ] Blog content exists at `/blog` ✅ (4 articles)
- [ ] Site has been live for a few days

### Application Steps
1. Go to [adsense.google.com](https://adsense.google.com)
2. Sign in with your Google account
3. Add your site domain
4. Add the AdSense verification `<script>` tag to `base.html` `<head>` section
5. Wait **1–14 days** for approval email

### After Approval — Replace Placeholders

**Publisher ID** — in every template file, replace:
```
ca-pub-XXXXXXXXXXXXXXXX
```
with your real publisher ID (e.g. `ca-pub-1234567890123456`)

Files to update:
- `templates/base.html` (line 13 — AdSense script src)
- `templates/index.html` (2 ad slots)
- `templates/about.html` (1 ad slot)
- `templates/privacy.html` (1 ad slot)
- `templates/blog.html` (1 ad slot)
- `templates/blog_watermark.html` (2 ad slots)
- `templates/blog_logo.html` (2 ad slots)
- `templates/blog_text.html` (2 ad slots)
- `templates/blog_inpainting.html` (2 ad slots)

**Ad Slot IDs** — replace the placeholder slot numbers with your real slot IDs from AdSense dashboard → Ads → By ad unit:

| Placeholder | Location | Ad Format |
|---|---|---|
| `1111111111` | Privacy page top | Auto/responsive |
| `2222222222` | About page top | Auto/responsive |
| `3333333333` | Homepage top | Auto/responsive |
| `4444444444` | Homepage mid (below tool) | Auto/responsive |
| `5555555555` | Blog index top | Auto/responsive |
| `6666666666` | All blog articles in-article | In-article fluid |
| `7777777777` | All blog articles bottom | Auto/responsive |

### Ad Placement Summary
| Page | Ad Slots |
|---|---|
| Homepage | Top banner + mid-page (below tool) |
| About | Top banner |
| Privacy | Top banner |
| Blog index | Top banner |
| Each blog article (×4) | In-article + bottom |

**Total ad slots: 13** across 8 pages.

### Revenue Projection (AdSense)

| Monthly Visitors | Estimated Revenue |
|---|---|
| 1,000 | ~$1–5 |
| 10,000 | ~$10–50 |
| 50,000 | ~$50–250 |
| 100,000 | ~$100–500 |

RPM (revenue per 1,000 views) for free tool sites: typically **$1–5**.
Growth is SEO-driven — blog articles target high-volume keywords.

---

## SEO Keywords Targeted

| Article | Target Keyword | Monthly Searches (est.) |
|---|---|---|
| `blog_watermark.html` | "remove watermark from image" | 40,000–100,000 |
| `blog_logo.html` | "remove logo from image online" | 10,000–30,000 |
| `blog_text.html` | "remove text from photo free" | 20,000–50,000 |
| `blog_inpainting.html` | "what is image inpainting" | 5,000–15,000 |

---

## Scaling Notes (When Traffic Grows)

| Trigger | Action |
|---|---|
| >500 concurrent users | Increase Gunicorn workers (`--workers 4`) |
| >1,000 req/min | Add nginx caching for static files |
| Processing too slow | Switch to `cv2.INPAINT_NS` (Navier-Stokes, slower but higher quality) or integrate LaMa |
| Storage filling up | Reduce auto-delete from 20 min to 5 min |
| Outgrowing VPS | Upgrade Contabo to next tier ($14/month: 8 vCPU, 16GB RAM) |

### To Upgrade to LaMa AI (Better Quality, Costs Money)
Replace `inpaint_image()` in `app.py` with a Replicate API call:
- Model: `zylim0702/remove-object` (get version hash from replicate.com/zylim0702/remove-object → API tab)
- Cost: ~$0.003–0.005 per image
- Requires: `REPLICATE_API_TOKEN` env var in Coolify

---

## Dependencies

```
flask>=3.0.0
python-dotenv>=1.0.0
requests>=2.31.0
Pillow>=10.0.0
numpy>=1.24.0
opencv-python-headless>=4.8.0
APScheduler>=3.10.0
gunicorn>=21.2.0
```

**opencv-python-headless** (not `opencv-python`) — required for headless server environments (no display).

---

## Security Notes
- Uploaded files validated by extension: `jpg, jpeg, png, webp` only
- Max upload size: 20MB (enforced by Flask)
- Files stored with UUID filenames — no path traversal possible
- Auto-deleted every 5 minutes (files older than 20 min)
- No user accounts, no database of user data, no cookies set by the app
- AdSense sets its own cookies (disclosed in Privacy Policy)
