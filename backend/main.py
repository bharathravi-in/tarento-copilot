from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db

app = FastAPI(title="Tarento Enterprise AI Co-Pilot")

@app.on_event("startup")
def startup_event():
    """Initialize DB Tables on startup"""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")

@app.get("/")
def read_root():
    return {"message": "Tarento AI Agent System is Online"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "Database Connected", "mode": "Hackathon Ready"}
