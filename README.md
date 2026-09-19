# RetinaScan

**AI-Powered Diabetic Retinopathy Screening System**

A clinical-grade screening tool that analyzes retinal fundus images to detect and grade Diabetic Retinopathy (DR) using deep learning and explainable AI.

---

## Overview

Diabetic Retinopathy is a leading cause of preventable blindness worldwide. Early detection is critical, but access to ophthalmologists is limited in rural and underserved regions.

**RetinaScan** provides an automated screening solution that:
- Accepts retinal fundus images via camera capture or file upload
- Classifies DR severity into 5 clinical grades
- Generates Grad-CAM heatmaps for explainability
- Produces AI-generated clinical explanations
- Auto-flags high-risk cases for specialist referral
- Persists patient records and predictions in a PostgreSQL database

The system is designed with a **rural-first, offline-capable** architecture and supports multiple Indian languages.

---

## Features

### Core Capabilities
- **5-Class DR Classification** — No DR, Mild, Moderate, Severe, Proliferative DR
- **Explainable AI** — Grad-CAM heatmaps highlighting regions of model attention
- **Multi-Language Support** — English, Hindi, Odia, Bengali
- **Auto-Referral Engine** — Flags Moderate/Severe/Proliferative cases
- **Patient Management** — Registration with diabetes type tracking
- **Prediction History** — Stored in PostgreSQL with timestamps
- **Invalid Image Detection** — Rejects non-retinal images before diagnosis

### Clinical Safety
- Confidence scores for every prediction
- Clear risk-level categorization
- AI-generated clinical explanations
- Referral recommendations aligned with DR staging guidelines

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI + Uvicorn |
| **Database** | PostgreSQL + SQLAlchemy |
| **AI Model** | TensorFlow 2.21 / Keras (ResNet50) |
| **Explainability** | Grad-CAM (custom implementation) |
| **Image Processing** | OpenCV, Pillow |
| **Frontend** | Streamlit |
| **Language** | Python 3.13 |

---

## Model Details

| Property | Value |
|---|---|
| **Architecture** | ResNet50 + GlobalAveragePooling + Dropout + Dense |
| **Input Size** | 224 × 224 × 3 (RGB) |
| **Output Classes** | 5 (No DR, Mild, Moderate, Severe, Proliferative DR) |
| **Preprocessing** | ResNet50-specific `preprocess_input` |
| **Training Dataset** | APTOS 2019 Blindness Detection |
| **Validation Accuracy** | ~79% |
| **Model Size** | 158 MB |
| **Explainability Layer** | `conv5_block3_out` (last conv layer) |


---

## Setup Instructions

### Prerequisites

- Python **3.13+**
- PostgreSQL **15+**
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/kashikaaa06/DR-Screening-.git
cd DR-Screening-
2. Create a Virtual Environment
bash
python -m venv .venv
Activate:

Windows: .venv\Scripts\activate

Mac/Linux: source .venv/bin/activate

3. Install Dependencies
bash
pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary pydantic pydantic-settings python-dotenv opencv-python tensorflow python-multipart pillow numpy streamlit requests
4. Download the Trained Model
The trained model (DR_ResNet50_Final.keras, 158 MB) is available under Releases.

Direct download:
DR_ResNet50_Final.keras

Place the downloaded file at:

text
ml-models/models/DR_ResNet50_Final.keras
5. Configure Environment Variables
Create a .env file in the project root:

env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/dr_screening
SECRET_KEY=change-this-to-a-random-secret
UPLOAD_DIR=app/static/uploads
GRADCAM_DIR=app/static/gradcam
MODEL_PATH=ml-models/models/DR_ResNet50_Final.keras
LAST_CONV_LAYER=conv5_block3_out
Replace YOUR_PASSWORD with your PostgreSQL password.

6. Set Up the Database
Create the database:

bash
psql -U postgres -h localhost
sql
CREATE DATABASE dr_screening;
\q
Tables are auto-created by SQLAlchemy on first backend startup.

7. Run the Backend
bash
uvicorn app.main:app
Backend runs at: http://localhost:8000
API documentation: http://localhost:8000/docs

8. Run the Frontend
Open a new terminal, activate the virtual environment, then:

bash
streamlit run frontend/streamlit_app.py
Frontend runs at: http://localhost:8501

API Endpoints
Method	Endpoint	Purpose
POST	/patients	Register a new patient
GET	/patients	List all patients
GET	/patients/{patient_id}	Fetch patient details
POST	/predict	Upload retinal image and get DR prediction
GET	/predictions	List all predictions
Sample Request
bash
curl -X POST http://localhost:8000/predict \
  -F "patient_id=<patient-uuid>" \
  -F "file=@retina.jpg"
Sample Response
json
{
  "prediction_id": "uuid",
  "patient_name": "John Doe",
  "patient_age": 55,
  "patient_gender": "Male",
  "patient_diabetes_type": "Type 2",
  "dr_grade": "Moderate",
  "detailed_grade": "Moderate Non-Proliferative DR (NPDR)",
  "confidence": 0.7512,
  "risk_level": "Moderate",
  "all_scores": {
    "No DR": 0.0005,
    "Mild": 0.0942,
    "Moderate": 0.7512,
    "Severe": 0.0460,
    "Proliferative DR": 0.1081
  },
  "image_url": "/static/uploads/xxx.jpg",
  "gradcam_url": "/static/gradcam/xxx_gradcam.jpg",
  "referral_needed": true,
  "not_retinal": false
}
Usage Workflow
Register Patient — Enter name, age, gender, diabetes type

Select Input Method — Camera capture or file upload

Capture/Upload Image — Provide a retinal fundus image

Run AI Diagnosis — Click to analyze

Review Result — DR grade, confidence, Grad-CAM heatmap, clinical explanation

Referral Flag — Automatic referral recommendation for high-risk cases

DR Grading Scale
Grade	Stage	Risk	Action
0	No DR	Low	Routine follow-up
1	Mild NPDR	Low	Annual screening
2	Moderate NPDR	Moderate	Ophthalmology referral
3	Severe NPDR	High	Urgent referral
4	Proliferative DR	Critical	Immediate intervention
Model Input Requirements
For accurate predictions, images must be:

Retinal fundus images (not external eye photos)

224 × 224 resolution (auto-resized)

Clear and well-lit

Centered optic disc

The system includes an image quality validator that rejects non-retinal images before inference.

Environment Notes
Tested on Windows with Python 3.13.15 and PostgreSQL 18.6

Model is loaded once at startup (30–60 seconds initial load time)

First prediction may take longer while TensorFlow warms up

Grad-CAM heatmaps are saved to app/static/gradcam/

License
This project is provided for research and educational purposes.

Acknowledgements
APTOS 2019 Blindness Detection dataset for model training

ResNet50 pretrained on ImageNet

Grad-CAM technique for model interpretability
