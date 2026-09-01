Lead Scoring Pro - ML Powered Lead Management System

An intelligent lead scoring system that uses Machine Learning to predict lead conversion probability. Built with FastAPI, React, and scikit-learn.

Python 3.11

FasAPI 0.109.0

React 18.2.0

sckitlearn 1.3.2

Supabase F2S4C4

Render


Features

ML Prediction - RandomForest classifier predicts Hot/Cold leads

Real-time Dashboard - Live statistics with pie chart

Webhook Integration - Auto-capture leads from any website

Authentication - Secure login/register with JWT

Database - PostgreSQL with SQLAlchemy ORM

Auto-tracking - Source, visits, time spent auto-captured

Professional UI - Clean, modern dark theme


Tech Stack

Layer	        Technology

Frontend	React 18, Vite, Inline Styles

Backend	        FastAPI, Uvicorn

Database	PostgreSQL (Supabase)

ML Model	scikit-learn (Random Forest)

Authentication	JWT, bcrypt

Deployment	Render (Docker)



📁*Project Structure

lead-scoring-project/

├── backend/

│ ├── main.py # FastAPI app

│ ├── models.py # SQLAlchemy models

│ ├── scoring.py # ML prediction

│ ├── train_model.py # Model training script

│ ├── requirements.txt # Python dependencies

│ ├── Dockerfile # Docker config

│ ├── .dockerignore

│ ├── real_model.pkl # Trained ML model

│ ├── model_columns.pkl # Model feature names

│ └── .env # Environment variables (gitignored)

│

├── frontend/

│ ├── package.json

│ ├── vite.config.js

│ ├── index.html

│ └── src/

│ ├── main.jsx

│ ├── App.jsx

│ ├── index.css

│ └── components/

│ ├── Login.jsx

│ └── Dashboard.jsx

│

├── form/

│ └── index.html # Public customer form

│

├── .gitignore

├── .gitattributes

└── README.md



## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.11+

- Node.js 18+

- Supabase account



\### 1. Clone Repository

```bash

git clone https://github.com/khurramks1111-vibe/Lead-Scoring-Pro.git

cd Lead-Scoring-Pro/backend



2. Setup Environment

python -m venv venv

venv\\Scripts\\activate  # Windows

source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt



3. Setup Database

Create project on Supabase

Run SQL from backend/setup\_db.sql in SQL Editor

Update backend/.env with your database credentials



4. Train ML Model (First time only)

python train\_model.py


5. Run Backend

uvicorn main:app --reload

6. Run Frontend

cd ../frontend

npm install

npm run dev

Access:

Frontend: http://localhost:5173

Backend API: http://localhost:8000

API Docs: http://localhost:8000/docs


🌐 Deployment (Render)

**Prerequisites**

* GitHub account
* Render account (free tier available)
* Supabase database already set up

Backend (Docker)

1. Go to Render.com

2. New > Web Service > GitHub repo

3. Settings:

Root Directory: backend

Runtime: Docker

Build: pip install -r requirements.txt

Start: uvicorn main:app --host 0.0.0.0 --port $PORT


4. Add environment variables:

DB_HOST=your-db-host.pooler.supabase.co

DB_PORT=6543

DB_NAME=postgres

DB_USER=postgres.project\_id

DB_PASS=your-password

SECRET_KEY=your-secret-key

ALGORITHM=HS256



Frontend (Static Site)

1. Update API URL in frontend/src/Login.jsx and frontend/src/Dashboard.jsx:

javascript

const API_BASE = 'https://your-backend.onrender.com'

2. New > Static Site > GitHub repo

3. Root Directory: frontend

4. Build: npm install && npm run build

5. Publish Directory: dist



Customer Form (Static Site)



1. New > Static Site > GitHub repo

2. Root Directory: form

3. Build Command: (empty)

4. Publish Directory: .

5. URL: https://your-form.onrender.com



📡 API Endpoints



Method       Endpoint        Auth Required          Description


GET	         /health	        ❌	                Health check       

POST	    /register	        ❌	                Create user

POST	    /login	            ❌	                Get JWT token

GET	        /leads/	            ✅	                Get all leads

POST	    /predict-lead	    ✅	                ML prediction + Save lead

POST	    /webhook/lead	    ❌	                Public webhook for forms

DELETE	    /leads/{id}	        ✅	                Delete a lead



📱 Customer Form Integration





https://your-form.onrender.com



🔐 How It Works



┌──────────┐     ┌──────────┐     ┌──────────┐

│  Website │────>│  Form    │────>│ Backend │

│  Ad/Social │     │  Submit │     │ API     │

└──────────┘     └──────────┘     └────┬───┘

                                        │

                                        ▼

                                 ┌──────────┐

                                 │   ML Model   │

                                 └──────────┘

                                        │

                             ┌─────────────────────┐

                             │    Hot Lead 🔥        │

                             │    OR               │

                             │    Cold Lead ❄️      │

                             └─────────────────────┘

                                        │

                             ┌──────────┐

                             │ Dashboard │

                             │ + Pie Chart │

                             │ + Table    │

                             └──────────┘

🛠️ Troubleshooting

Database Connection Failed

* Check .env file exists with correct Supabase credentials
* Use Transaction pooler connection string (port 6543)
* Ensure SSL mode is enabled

CORS Error

* Ensure allow\_origins includes frontend URL
* Use direct CORS headers in endpoint


Model Version Warning

* Retrain model with current scikit-learn version
* Both versions must match



Port 8000 not working (Render)



* Use $PORT in Dockerfile CMD
* Check Render environment variables

📱 License

This project is open source under the MIT License.

📧 Contact

GitHub: Lead-Scoring-Pro

Built with ❤️ using Python, React, FastAPI, scikit-learn, and Supabase

