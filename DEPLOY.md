# TrainSmart — Deployment Guide (Google Cloud)

## Architecture

```
Browser → Cloud Run (FastAPI) → Algorithm (Python) → Cloud SQL (PostgreSQL)
```

## Project Structure

```
trainingsapp/
├── main.py                   # FastAPI app & routes
├── database.py               # Cloud SQL / SQLite connector
├── algorithm/
│   ├── __init__.py
│   └── trainingsplan.py      # Jouw algoritme (ongewijzigd)
├── templates/
│   └── index.html            # Frontend HTML
├── static/
│   ├── css/style.css
│   └── js/app.js
├── requirements.txt
├── Dockerfile
├── cloudbuild.yaml           # Cloud Build CI/CD
└── DEPLOY.md
```

---

## 1. Lokaal draaien

```bash
cd trainingsapp
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
# Open: http://localhost:8080
```

---

## 2. Cloud SQL opzetten

```bash
# Maak een PostgreSQL instantie aan
gcloud sql instances create trainingsapp-db \
  --database-version=POSTGRES_15 \
  --region=europe-west4 \
  --tier=db-f1-micro   # Kleinste optie, goedkoopst

# Maak database en gebruiker aan
gcloud sql databases create trainingsapp --instance=trainingsapp-db
gcloud sql users create trainingsapp_user \
  --instance=trainingsapp-db \
  --password=JOUW_WACHTWOORD

# Sla wachtwoord op in Secret Manager
echo -n "JOUW_WACHTWOORD" | gcloud secrets create db-password --data-file=-
```

---

## 3. Artifact Registry

```bash
gcloud artifacts repositories create trainingsapp \
  --repository-format=docker \
  --location=europe-west4

gcloud auth configure-docker europe-west4-docker.pkg.dev
```

---

## 4. Handmatig bouwen & deployen

```bash
# Bouw en push image
docker build -t europe-west4-docker.pkg.dev/PROJECT_ID/trainingsapp/trainingsapp:latest .
docker push europe-west4-docker.pkg.dev/PROJECT_ID/trainingsapp/trainingsapp:latest

# Deploy naar Cloud Run
gcloud run deploy trainingsapp \
  --image=europe-west4-docker.pkg.dev/PROJECT_ID/trainingsapp/trainingsapp:latest \
  --region=europe-west4 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="CLOUD_SQL_INSTANCE_CONNECTION_NAME=PROJECT:europe-west4:trainingsapp-db,DB_NAME=trainingsapp,DB_USER=trainingsapp_user" \
  --set-secrets="DB_PASS=db-password:latest" \
  --add-cloudsql-instances=PROJECT:europe-west4:trainingsapp-db \
  --memory=512Mi
```

---

## 5. CI/CD via Cloud Build

```bash
# Verbind je GitHub repo in de Cloud Console:
# Cloud Build → Triggers → Connect Repository

# Of trigger handmatig:
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_CLOUD_SQL_INSTANCE="PROJECT:europe-west4:trainingsapp-db"
```

---

## 6. Omgevingsvariabelen

| Variabele                         | Beschrijving                        |
|-----------------------------------|-------------------------------------|
| `CLOUD_SQL_INSTANCE_CONNECTION_NAME` | `project:region:instance`        |
| `DB_NAME`                         | Database naam (`trainingsapp`)      |
| `DB_USER`                         | Database gebruiker                  |
| `DB_PASS`                         | Wachtwoord (via Secret Manager)     |

> **Zonder Cloud SQL** valt de app automatisch terug op SQLite (voor lokaal testen).

---

## 7. requirements.txt aanpassen voor Cloud SQL

Verwijder de commentaar `#` voor de Cloud SQL packages:

```
cloud-sql-python-connector[pg8000]==1.12.1
pg8000==1.31.2
```

---

## API Endpoints

| Methode | Pad                      | Beschrijving                        |
|---------|--------------------------|-------------------------------------|
| GET     | `/`                      | Frontend                            |
| POST    | `/api/trainingsplan`     | Genereer nieuw plan                 |
| GET     | `/api/trainingsplan/{id}`| Haal plan op via ID                 |
| GET     | `/api/trainingsplannen`  | Laatste 20 plannen                  |
| GET     | `/health`                | Health check voor Cloud Run         |
| GET     | `/docs`                  | Automatische Swagger API docs       |
