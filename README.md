# 🔥 Lead Scoring Pro

ML-powered lead scoring system that predicts **Hot / Cold** leads using a RandomForest model trained on the X Education leads dataset (65 one-hot features). Includes a custom-built **live event tracking system** — behavioral data (visits, time on site, page views, UTM attribution) is captured first-party in our own database and feeds directly into scoring.

---

## 🌐 Live URLs

| Service | URL |
|---|---|
| Frontend (Dashboard) | https://lead-scoring-4479-frontend.onrender.com |
| Backend (FastAPI) | https://lead-scoring-4479-backend.onrender.com |
| Lead Form (Public) | https://lead-scoring-4479-form.onrender.com |

---

## 🛠 Tech Stack

- **Backend:** FastAPI 0.109 (Docker, Render) · scikit-learn 1.3.2 · JWT auth
- **Frontend:** React 18.2 + Vite (dark-themed dashboard, live polling)
- **Database:** PostgreSQL (Supabase) via SQLAlchemy
- **Form:** Static HTML + custom first-party tracking script (no GA4/Mixpanel)

---

## ✨ Features

### 1. ML Lead Scoring
- RandomForest model predicts Hot 🔥 / Cold ❄️ per lead
- Duplicate leads are **updated + re-scored** on resubmission (not skipped)

### 2. Live Event Tracking (first-party)
- Events: page_view, page_exit (time_on_page + scroll_depth), form_start, field_focus, form_submit
- Session + UTM persistence via localStorage
- Beacons via navigator.sendBeacon (cross-origin safe) with fetch fallback
- Events linked to leads on form submit

### 3. Behavioral Scoring (server-side, authoritative)
- 30-min gap rule for visit counting (GA standard)
- 5s dedupe for rapid page_views, time capped at 3600s per exit
- UTM/referrer mapped to valid model Lead Source categories (Google, Direct Traffic, Organic Search, Pay per Click Ads, Social Media, Facebook, ...)

### 4. Dashboard
- Hot/Cold stats + pie chart
- Add New Lead form (ML prediction)
- Recent Leads table with Lead Source
- 📡 **Live Events Feed** — last 25 events, auto-refresh every 5s

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /health | — | Health check |
| POST | /register, /login | — | JWT auth |
| GET | /me | JWT | Current user |
| GET | /leads/ | JWT | All leads |
| POST | /predict-lead | JWT | Predict + save/update lead |
| POST | /webhook/lead | — | Public form submission (behavior-based scoring) |
| POST | /track | — | Event beacons |
| GET | /events/recent | JWT | Last 25 events (dashboard feed) |

---

## 📁 Project Structure

| Path | Description |
|---|---|
| backend/main.py | FastAPI app — endpoints, tracking, webhook, source mapping |
| backend/models.py | SQLAlchemy models — User, Lead, Event |
| backend/real_model.pkl | Trained RandomForest model |
| backend/model_columns.pkl | 65 one-hot feature columns |
| frontend/src/config.js | API_BASE (single source of truth) |
| frontend/src/Dashboard.jsx | Dashboard — stats, forms, leads table, live events feed |
| frontend/src/Login.jsx | Login page |
| form/index.html | Public form + tracking script |

---

## 🧪 Testing Guide

1. Open the form (use **Incognito** for fresh sessions)
2. Scroll, focus fields, submit with a new email
3. Login to the dashboard → lead appears with Hot/Cold + source
4. Events appear in Live Events Feed within 5s
5. **UTM test:** ?utm_source=facebook&utm_medium=cpc → "Pay per Click Ads"; without medium → "Facebook"; no UTM → "Direct Traffic"
6. **Duplicate test:** resubmit an existing email → lead updates + re-scores
