from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
from datetime import datetime

from algorithm.trainingsplan import genereer_trainingsplan
from database import get_db, save_trainingsplan, get_trainingsplan, get_all_plans

app = FastAPI(
    title="Trainingsplan Generator",
    description="API voor gepersonaliseerde trainingsplannen",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- Pydantic Models ---

class GebruikerInput(BaseModel):
    naam: str = Field(..., example="Jan de Vries")
    leeftijd: int = Field(..., ge=10, le=100, example=24)
    geslacht: str = Field(..., example="man")
    lengte: int = Field(..., ge=100, le=250, example=180)
    gewicht: float = Field(..., ge=30, le=300, example=80)
    trainingsdoel: str = Field(..., example="spieropbouw")
    trainingsniveau: str = Field(..., example="beginner")
    trainingsfrequentie: int = Field(..., ge=1, le=7, example=3)
    trainingsduur: int = Field(..., ge=15, le=180, example=60)
    activiteitsniveau: str = Field(..., example="gemiddeld")
    blessures: List[str] = Field(default=[], example=[])
    beschikbare_dagen: List[str] = Field(..., example=["maandag", "woensdag", "vrijdag"])


class TrainingsPlanResponse(BaseModel):
    id: Optional[int]
    naam: str
    schema_type: str
    focus: str
    sets: int
    herhalingen: str
    aantal_oefeningen_per_training: int
    intensiteit: str
    rusttijd: str
    activiteitsaanpassing: str
    vermijd_oefeningen: List[str]
    trainingsdagen: List[str]
    aangemaakt_op: Optional[str]


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/trainingsplan", response_model=TrainingsPlanResponse)
async def maak_trainingsplan(gebruiker: GebruikerInput):
    """Genereer een gepersonaliseerd trainingsplan op basis van gebruikersgegevens."""
    gebruiker_dict = gebruiker.dict()
    plan = genereer_trainingsplan(gebruiker_dict)

    # Save to database
    plan_id = None
    try:
        plan_id = save_trainingsplan(gebruiker_dict["naam"], gebruiker_dict, plan)
    except Exception as e:
        print(f"Database save error (non-fatal): {e}")

    return TrainingsPlanResponse(
        id=plan_id,
        naam=gebruiker_dict["naam"],
        aangemaakt_op=datetime.now().strftime("%d-%m-%Y %H:%M"),
        **plan
    )


@app.get("/api/trainingsplan/{plan_id}", response_model=TrainingsPlanResponse)
async def haal_trainingsplan_op(plan_id: int):
    """Haal een opgeslagen trainingsplan op via ID."""
    plan = get_trainingsplan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Trainingsplan niet gevonden")
    return plan


@app.get("/api/trainingsplannen")
async def haal_alle_plannen():
    """Haal de laatste 20 gegenereerde trainingsplannen op."""
    return get_all_plans()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
