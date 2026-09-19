from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import uuid
import shutil

from app.config import settings
from app.database import get_db, Patient, Prediction
from app.services.predictor import predict_dr

app = FastAPI(title="DR Screening API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.GRADCAM_DIR, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/static/gradcam", StaticFiles(directory=settings.GRADCAM_DIR), name="gradcam")

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    diabetes_type: str

@app.get("/")
def root():
    return {"status": "DR Screening API v2.0", "docs": "/docs"}

@app.post("/patients")
def create_patient(data: PatientCreate, db: Session = Depends(get_db)):
    p = Patient(name=data.name, age=data.age, gender=data.gender, diabetes_type=data.diabetes_type)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"patient_id": p.id, "message": "Patient created"}

@app.get("/patients")
def list_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return {"patients": [
        {"id": p.id, "name": p.name, "age": p.age, "gender": p.gender, "diabetes_type": p.diabetes_type}
        for p in patients
    ]}

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(404, "Patient not found")
    return {
        "id": p.id,
        "name": p.name,
        "age": p.age,
        "gender": p.gender,
        "diabetes_type": p.diabetes_type
    }

@app.post("/predict")
async def predict(patient_id: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "Patient not found")

    image_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{image_id}{ext}"
    path = os.path.join(settings.UPLOAD_DIR, filename)

    with open(path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    try:
        result = predict_dr(path)
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {str(e)}")

    explanations = result.get("explanations", {})
    english_explanation = explanations.get("English", "")

    pred = Prediction(
        patient_id=patient_id,
        image_path=filename,
        gradcam_path=result.get("gradcam_filename"),
        dr_grade=result["grade"],
        confidence=result["confidence"],
        risk_level=result["risk_level"],
        all_scores=str(result["all_scores"]),
        explanation=english_explanation
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    return {
        "prediction_id": pred.id,
        "patient_name": patient.name,
        "patient_age": patient.age,
        "patient_gender": patient.gender,
        "patient_diabetes_type": patient.diabetes_type,
        "dr_grade": result["grade"],
        "detailed_grade": result.get("detailed_grade", result["grade"]),
        "confidence": result["confidence"],
        "risk_level": result["risk_level"],
        "all_scores": result["all_scores"],
        "image_url": f"/static/uploads/{filename}",
        "gradcam_url": f"/static/gradcam/{result['gradcam_filename']}" if result.get("gradcam_filename") else None,
        "explanations": explanations,
        "referral_needed": result["risk_level"] in ["Moderate", "High"],
        "not_retinal": result.get("not_retinal", False)
    }

@app.get("/predictions")
def list_predictions(db: Session = Depends(get_db)):
    preds = db.query(Prediction).order_by(Prediction.created_at.desc()).all()
    return {"predictions": [
        {
            "id": p.id,
            "patient_id": p.patient_id,
            "dr_grade": p.dr_grade,
            "confidence": p.confidence,
            "risk_level": p.risk_level,
            "image_url": f"/static/uploads/{p.image_path}",
            "gradcam_url": f"/static/gradcam/{p.gradcam_path}" if p.gradcam_path else None
        }
        for p in preds
    ]}