from fastapi import FastAPI, Depends, Request, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv
import models
from scoring import predict_real_lead

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI(title="Lead Scoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lead-scoring-4479-frontend.onrender.com",
                   "https://lead-scoring-4479-form.onrender.com",
                   "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = auth.split("Bearer ")[1]
    credentials_exception = HTTPException(status_code=401, detail="Invalid token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise credentials_exception
    return user

# ================= LIVE TRACKING (naya) =================

ALLOWED_EVENTS = {"page_view", "page_exit", "form_start", "field_focus", "form_submit"}

def map_lead_source(utm_source, referrer, medium=""):
    """utm/referrer ko valid Lead Source category mein map karo"""
    u = (utm_source or "").strip().lower()
    r = (referrer or "").lower()
    m = (medium or "").strip().lower()
    if m in ("cpc", "ppc", "paid", "ads"):
        return "Pay per Click Ads"
    if u in ("google", "googleads", "adwords"):
        return "Google"
    if u == "bing":
        return "bing"
    if u in ("facebook", "fb", "instagram", "ig"):
        return "Facebook"
    if u == "youtube":
        return "youtubechannel"
    if u == "blog":
        return "blog"
    if u in ("linkedin", "twitter", "x", "tiktok", "pinterest", "whatsapp"):
        return "Social Media"
    if "google." in r or "bing." in r or "duckduckgo" in r:
        return "Organic Search"
    if any(s in r for s in ("facebook.com", "instagram.com", "t.co", "linkedin.com", "youtube.com", "twitter.com")):
        return "Social Media"
    if r:
        return "Referral Sites"
    return "Direct Traffic"

def compute_behavior(db, session_id: str):
    """Session ke events se REAL ML features nikaalo (server-side, authoritative)"""
    evs = db.query(models.Event).filter(models.Event.session_id == session_id).all()
    if not evs:
        return None
    page_views = [e for e in evs if e.event == "page_view"]
    days = {e.created_at.date() for e in page_views if e.created_at}
    visits = max(len(days), 1)
    time_spent = sum(int((e.props or {}).get("time_on_page") or 0)
                     for e in evs if e.event == "page_exit")
    first = page_views[0] if page_views else None
    return {
        "TotalVisits": visits,
        "Total Time Spent on Website": time_spent,
        "Page Views Per Visit": round(len(page_views) / visits, 1),
        "utm_source": first.utm_source if first else None,
        "referrer": first.referrer if first else None,
    }

@app.post("/track")
async def track_event(request: Request, db: Session = Depends(get_db)):
    # text/plain beacon support (sendBeacon cross-origin ke liye zaroori)
    try:
        p = json.loads(await request.body())
    except Exception:
        return Response(status_code=204)

    sid = str(p.get("session_id", ""))[:64]
    event = str(p.get("event", ""))[:50]
    if not sid.startswith("s_") or event not in ALLOWED_EVENTS:
        return Response(status_code=204)

    props = p.get("props") or {}
    if not isinstance(props, dict):
        props = {}

    db.add(models.Event(
        session_id=sid, event=event, props=props,
        url=str(p.get("url") or "")[:500],
        referrer=str(p.get("referrer") or "")[:500],
        utm_source=str(p.get("utm_source") or "")[:100],
    ))
    db.commit()
    return Response(status_code=204)

@app.get("/events/recent")
def recent_events(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    rows = db.query(models.Event).order_by(models.Event.created_at.desc()).limit(25).all()
    return [
        {
            "event": r.event, "url": r.url, "props": r.props,
            "session_id": r.session_id[:10] + "…",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]

# ================= ORIGINAL ENDPOINTS =================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

@app.get("/health")
def health_check():
    try:
        db = models.SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists!")
    new_user = models.User(username=data.username, hashed_password=get_password_hash(data.password))
    db.add(new_user)
    db.commit()
    return {"message": "User created!"}

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "username": user.username}

@app.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {"username": current_user.username}

@app.get("/leads/")
def get_leads(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    leads = db.query(models.Lead).order_by(models.Lead.created_at.desc()).all()
    return {"total_leads": len(leads), "data": leads}

@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found!")
    db.delete(lead)
    db.commit()
    return {"message": "Lead deleted!"}

@app.post("/predict-lead")
async def predict_lead(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        form_data = await request.json()
        ml_result = predict_real_lead(form_data)
        existing = db.query(models.Lead).filter(models.Lead.email == form_data.get("email")).first()
        if existing:
            return {"message": f"Prediction: {ml_result} (Email exists)", "prediction": ml_result, "saved": False}
        new_lead = models.Lead(
            name=form_data.get("name"),
            email=form_data.get("email"),
            lead_origin=form_data.get("Lead Origin"),
            total_visits=int(form_data.get("TotalVisits", 0)),
            time_spent=int(form_data.get("Total Time Spent on Website", 0)),
            page_views=float(form_data.get("Page Views Per Visit", 0)),
            occupation=form_data.get("What is your current occupation"),
            is_converted="Hot" in ml_result
        )
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        return {"message": f"{new_lead.name} - {ml_result}", "prediction": ml_result, "saved": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/lead")
async def webhook_lead(request: Request, db: Session = Depends(get_db)):
    """Customer form — ab REAL behavioral data ke saath"""
    try:
        data = await request.json()
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        if not name or not email:
            raise HTTPException(status_code=400, detail="Name and email required")

        session_id = (data.get("session_id") or "").strip()

        # --- Behavioral data: events se (authoritative), warna client fallback ---
        behavior = compute_behavior(db, session_id) if session_id else None
        total_visits = behavior["TotalVisits"] if behavior else int(data.get("visits", 0) or 0)
        time_spent = behavior["Total Time Spent on Website"] if behavior else int(data.get("time_spent", 0) or 0)
        page_views = behavior["Page Views Per Visit"] if behavior else float(data.get("page_views", 0) or 0)

        utm_source = data.get("utm_source") or (behavior and behavior.get("utm_source"))
        referrer = data.get("referrer") or (behavior and behavior.get("referrer"))
        lead_source = map_lead_source(utm_source, referrer, data.get("utm_medium"))
        lead_origin = "Landing Page Submission"

        form_for_ml = {
            "name": name,
            "email": email,
            "Lead Origin": lead_origin,
            "Lead Source": lead_source,
            "Last Activity": "Form Submitted on Website",
            "Last Notable Activity": "Form Submitted on Website",
            "What is your current occupation": data.get("occupation") or "Unknown",
            "TotalVisits": total_visits,
            "Total Time Spent on Website": time_spent,
            "Page Views Per Visit": page_views,
        }

        ml_result = predict_real_lead(form_for_ml)

        existing = db.query(models.Lead).filter(models.Lead.email == email).first()
        if existing:
            return {"status": "duplicate", "prediction": ml_result}

        new_lead = models.Lead(
            name=name, email=email,
            lead_origin=lead_origin, source=lead_source,
            total_visits=total_visits, time_spent=time_spent,
            page_views=page_views,
            occupation=data.get("occupation") or "Unknown",
            is_converted="Hot" in ml_result,
        )
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)

        # Events ko lead se link karo
        if session_id:
            db.query(models.Event).filter(
                models.Event.session_id == session_id,
                models.Event.lead_id.is_(None)
            ).update({"lead_id": new_lead.id}, synchronize_session=False)
            db.commit()

        return {"status": "success", "prediction": ml_result, "message": f"{name} - {ml_result}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
def startup():
    print("🔄 Checking database...")
    try:
        db = models.SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connected!")
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)