🔥 Lead Scoring Pro
ML-powered lead scoring system that predicts Hot / Cold leads using a RandomForest model trained on the X Education leads dataset (65 one-hot features). Includes a custom-built live event tracking system — behavioral data (visits, time on site, page views, UTM attribution) is captured first-party in our own database and feeds directly into scoring.

🌐 Live URLs
Service	URL
Frontend (Dashboard)	https://lead-scoring-4479-frontend.onrender.com
Backend (FastAPI)	https://lead-scoring-4479-backend.onrender.com
Lead Form (Public)	https://lead-scoring-4479-form.onrender.com
Repository	github.com/khurramshahzad4479/Lead-Scoring-Project
🛠 Tech Stack
Backend: FastAPI 0.109 (Docker, Render) · scikit-learn 1.3.2 · JWT auth
Frontend: React 18.2 + Vite (dark-themed dashboard, live polling)
Database: PostgreSQL (Supabase, ap-southeast-2) via SQLAlchemy
Form: Static HTML + custom first-party tracking script (no GA4/Mixpanel)
Keep-alive: cron-job.org pings /health every 10 min (Render free tier)
✨ Features
1. ML Lead Scoring
RandomForest model (real_model.pkl + model_columns.pkl, 65 one-hot features)
Predicts Hot 🔥 / Cold ❄️ per lead, saved to DB
Duplicate leads are updated + re-scored (not skipped) — new form submissionsoverwrite name, source, behavior data, occupation, and prediction
2. Live Event Tracking (first-party)
page_view, page_exit (time_on_page + scroll_depth), form_start, field_focus, form_submit events
Session ID via localStorage (lspro_sid), UTM persistence (lspro_utm_*)
Sent via navigator.sendBeacon (Blob type text/plain for cross-origin) with fetch keepalive fallback
Events linked to lead_id on form submit
Dashboard shows a 📡 Live Events Feed (last 25 events, 5s auto-refresh)
3. Behavioral Scoring (server-side, authoritative)
30-min gap rule for counting visits (GA standard)
5s dedupe for rapid page_views
Time on page capped at 3600s per exit
UTM/referrer → valid X Education Lead Source categories (see mapping below)
Client-side values used only as fallback
4. UTM / Lead Source Attribution
Incoming signal	Mapped Lead Source
utm_medium in cpc/ppc/paid/ads	Pay per Click Ads
utm_source google/googleads/adwords	Google
utm_source bing / blog / youtube	bing / blog / youtubechannel
utm_source facebook/fb/instagram/ig	Facebook
utm_source linkedin/twitter/tiktok/…	Social Media
Search engine referrer	Organic Search
Social site referrer	Social Media
Any other referrer	Referral Sites
Nothing	Direct Traffic
All mapped values are verified against model_columns.pkl — every category is a real one-hot feature in the model.

🔌 API Endpoints
Method	Endpoint	Auth	Description
GET	/health	—	Health check (cron ping target)
POST	/register, /login	—	JWT auth
GET	/me	JWT	Current user
GET	/leads/	JWT	All leads (incl. source, behavior fields)
POST	/predict-lead	JWT	Dashboard form → predict, save/update + re-score
POST	/webhook/lead	—	Public form → behavior-based predict + save/update
POST	/track	—	Event beacons (text/plain, whitelist, s_ prefix check)
GET	/events/recent	JWT	Last 25 events (dashboard feed)
📁 Project Structure
├── backend/
│ ├── main.py # endpoints, tracking, webhook, mapping
│ ├── models.py # User, Lead, Event (JSONB props)
│ ├── real_model.pkl # trained RandomForest
│ └── model_columns.pkl# 65 feature columns
├── frontend/
│ └── src/
│ ├── config.js # ⭐ API_BASE — single source of truth
│ ├── Dashboard.jsx# stats, add-lead form, leads table, live events feed
│ └── Login.jsx
└── form/
└── index.html # public form + tracking script


---

## 🧪 Testing Guide

1. Open the form (use **Incognito** for fresh sessions)
2. Scroll, focus fields, submit with a new email
3. Login to the dashboard → lead appears with Hot/Cold + source
4. Events appear in Live Events Feed within 5s
5. **UTM test:** `?utm_source=facebook&utm_medium=cpc` → "Pay per Click Ads"; 
   without medium → "Facebook"; no UTM → "Direct Traffic"
6. **Duplicate test:** resubmit an existing email → lead updates + re-scores