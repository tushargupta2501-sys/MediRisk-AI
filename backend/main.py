from contextlib import asynccontextmanager
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import xgboost as xgb

try:
    from backend.schemas import PatientData
except ImportError:
    from schemas import PatientData


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

PREPROCESSOR_PATH = (
    BASE_DIR.parent / "model" / "medirisk_preprocessor.joblib"
)

XGB_MODEL_PATH = (
    BASE_DIR.parent / "model" / "medirisk_xgb.json"
)

JSON_PATH = BASE_DIR / "predictions.json"


# ------------------------------------------------------------
# Model loading with robust error handling
# ------------------------------------------------------------
preprocessor = None
xgb_model = None
model_load_error: str | None = None


def load_artifacts() -> None:
    """
    Loads the fitted scikit-learn preprocessor and the native XGBoost model.
    Captures descriptive errors if files are missing or unreadable.
    """
    global preprocessor, xgb_model, model_load_error

    if not PREPROCESSOR_PATH.exists():
        model_load_error = f"Preprocessor file not found at: {PREPROCESSOR_PATH}"
        preprocessor = None
        return

    if not XGB_MODEL_PATH.exists():
        model_load_error = f"XGBoost model file not found at: {XGB_MODEL_PATH}"
        xgb_model = None
        return

    try:
        preprocessor = joblib.load(PREPROCESSOR_PATH)
    except Exception as e:
        model_load_error = f"Failed to load preprocessor artifact: {str(e)}"
        preprocessor = None
        return

    try:
        loaded_booster = xgb.Booster()
        loaded_booster.load_model(str(XGB_MODEL_PATH))
        xgb_model = loaded_booster
    except Exception as e:
        model_load_error = f"Failed to load XGBoost model artifact: {str(e)}"
        xgb_model = None
        return

    model_load_error = None


# Attempt loading artifacts immediately on import
load_artifacts()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure artifacts are loaded on application startup
    if preprocessor is None or xgb_model is None:
        load_artifacts()
    yield


app = FastAPI(
    title="MediRisk AI",
    description="Cardiovascular risk prediction API powered by XGBoost",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------
@app.get("/")
def home() -> Dict[str, str]:
    """Health check endpoint to verify API availability."""
    return {
        "message": "MediRisk AI API is running"
    }


@app.post("/predict")
def predict(patient: PatientData) -> Dict[str, Any]:
    """
    Generate cardiovascular risk prediction for a patient.
    
    Prediction flow:
    Patient JSON -> Pydantic validation -> pandas DataFrame ->
    saved preprocessor -> XGBoost DMatrix -> XGBoost model ->
    risk probability -> binary prediction -> JSON history
    """
    # Verify model readiness
    if preprocessor is None or xgb_model is None:
        # Attempt reloading in case artifacts were added or updated
        load_artifacts()
        if preprocessor is None or xgb_model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Model artifacts unavailable: {model_load_error}"
            )

    try:
        # Convert validated Pydantic data into dictionary and 1-row DataFrame
        patient_data = patient.model_dump()
        input_data = pd.DataFrame([patient_data])

        # Apply saved sklearn preprocessing pipeline
        processed_data = preprocessor.transform(input_data)

        # Convert to XGBoost DMatrix and compute probability
        dmatrix = xgb.DMatrix(processed_data)
        probability = float(xgb_model.predict(dmatrix)[0])

        # Binary prediction using threshold 0.5
        prediction = int(probability >= 0.5)
        rounded_probability = round(probability, 4)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inference processing failed: {str(e)}"
        )

    # Save prediction history to JSON_PATH
    record = {
        "patient": patient_data,
        "risk_probability": rounded_probability,
        "prediction": prediction,
        "created_at": datetime.now().isoformat()
    }

    records: List[Dict[str, Any]] = []
    if JSON_PATH.exists():
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as file:
                content = file.read().strip()
                if content:
                    loaded = json.loads(content)
                    if isinstance(loaded, list):
                        records = loaded
        except json.JSONDecodeError:
            # Corrupted predictions.json: gracefully recover by creating a new list
            records = []
        except Exception:
            records = []

    records.append(record)

    try:
        with open(JSON_PATH, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=4)
    except Exception as e:
        # Even if logging history fails, log error but do not fail prediction output
        print(f"Warning: Failed to persist prediction to {JSON_PATH}: {e}")

    return {
        "risk_probability": rounded_probability,
        "prediction": prediction,
        "message": "Prediction completed successfully"
    }


@app.get("/predictions")
def get_predictions() -> List[Dict[str, Any]]:
    """Return all previously stored predictions from predictions.json."""
    if not JSON_PATH.exists():
        return []

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return []
            records = json.loads(content)
            if not isinstance(records, list):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Predictions history format is invalid (expected a JSON array)."
                )
            return records
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Predictions history file is corrupted."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read predictions history: {str(e)}"
        )
