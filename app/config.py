import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "app/static/uploads")
    GRADCAM_DIR = os.getenv("GRADCAM_DIR", "app/static/gradcam")
    MODEL_PATH = os.getenv("MODEL_PATH", "ml-models/models/DR_ResNet50_Final.keras")
    LAST_CONV_LAYER = os.getenv("LAST_CONV_LAYER", "conv5_block3_out")

settings = Settings()