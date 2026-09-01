from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
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
    allow_origins=["*"],
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
    """Simple form - only name, email, phone, message needed"""
    try:
        data = await request.json()
        
        # Only these are required from customer
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        
        if not name or not email:
            raise HTTPException(status_code=400, detail="Name and email required")
        
        # Everything else is AUTO-FILLED or has defaults
        form_for_ml = {
            "name": name,
            "email": email,
            "Lead Origin": data.get("source", "Website Form"),
            "Lead Source": data.get("medium", "Direct"),
            "What is your current occupation": data.get("occupation", "Unknown"),
            "TotalVisits": data.get("visits", 0),
            "Total Time Spent on Website": data.get("time_spent", 0),
            "Page Views Per Visit": data.get("page_views", 0)
        }
        
        # ML Prediction
        ml_result = predict_real_lead(form_for_ml)
        
        # Duplicate check
        existing = db.query(models.Lead).filter(models.Lead.email == email).first()
        if existing:
            return {"status": "duplicate", "prediction": ml_result}
        
        # Save
        new_lead = models.Lead(
            name=name,
            email=email,
            lead_origin=data.get("source", "Website Form"),
            source=data.get("medium", "Direct"),
            total_visits=int(data.get("visits", 0)),
            time_spent=int(data.get("time_spent", 0)),
            page_views=float(data.get("page_views", 0)),
            occupation=data.get("occupation", "Unknown"),
            is_converted="Hot" in ml_result
        )
        db.add(new_lead)
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
