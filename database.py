"""
Database module - Cloud SQL (PostgreSQL) via Cloud SQL Connector
Falls back to SQLite for local development when Cloud SQL is not configured.
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List

# Try to import Cloud SQL connector
try:
    from google.cloud.sql.connector import Connector
    import sqlalchemy
    CLOUD_SQL_AVAILABLE = True
except ImportError:
    CLOUD_SQL_AVAILABLE = False

# Environment variables for Cloud SQL
CLOUD_SQL_INSTANCE = os.environ.get("CLOUD_SQL_INSTANCE_CONNECTION_NAME")  # project:region:instance
DB_NAME = os.environ.get("DB_NAME", "trainingsapp")
DB_USER = os.environ.get("DB_USER", "trainingsapp_user")
DB_PASS = os.environ.get("DB_PASS", "")

# SQLite fallback for local development
SQLITE_PATH = os.environ.get("SQLITE_PATH", "trainingsapp.db")

_engine = None
_connector = None


def _get_cloud_sql_engine():
    """Create Cloud SQL connection engine using the Cloud SQL Connector."""
    global _connector
    _connector = Connector()

    def getconn():
        conn = _connector.connect(
            CLOUD_SQL_INSTANCE,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
        )
        return conn

    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return engine


def _get_sqlite_engine():
    """Create SQLite engine for local development."""
    engine = sqlalchemy.create_engine(f"sqlite:///{SQLITE_PATH}")
    return engine


def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        if CLOUD_SQL_AVAILABLE and CLOUD_SQL_INSTANCE:
            try:
                _engine = _get_cloud_sql_engine()
                print("✅ Connected to Cloud SQL")
            except Exception as e:
                print(f"⚠️  Cloud SQL failed ({e}), falling back to SQLite")
                _engine = _get_sqlite_engine()
        else:
            print("📁 Using SQLite (local development)")
            _engine = _get_sqlite_engine()
    return _engine


def init_db():
    """Initialize database tables."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS trainingsplannen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                naam TEXT NOT NULL,
                gebruiker_data TEXT NOT NULL,
                plan_data TEXT NOT NULL,
                aangemaakt_op TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()


def get_db():
    """Dependency for FastAPI routes."""
    engine = get_engine()
    return engine


def save_trainingsplan(naam: str, gebruiker_data: Dict, plan_data: Dict) -> int:
    """Save a training plan to the database. Returns the new plan ID."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                sqlalchemy.text("""
                    INSERT INTO trainingsplannen (naam, gebruiker_data, plan_data, aangemaakt_op)
                    VALUES (:naam, :gebruiker_data, :plan_data, :aangemaakt_op)
                """),
                {
                    "naam": naam,
                    "gebruiker_data": json.dumps(gebruiker_data),
                    "plan_data": json.dumps(plan_data),
                    "aangemaakt_op": datetime.now().isoformat(),
                }
            )
            conn.commit()
            return result.lastrowid
    except Exception as e:
        print(f"DB save error: {e}")
        return None


def get_trainingsplan(plan_id: int) -> Optional[Dict]:
    """Retrieve a training plan by ID."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                sqlalchemy.text("SELECT * FROM trainingsplannen WHERE id = :id"),
                {"id": plan_id}
            ).fetchone()
            if result:
                plan_data = json.loads(result[3])
                return {
                    "id": result[0],
                    "naam": result[1],
                    "aangemaakt_op": result[4],
                    **plan_data
                }
    except Exception as e:
        print(f"DB fetch error: {e}")
    return None


def get_all_plans(limit: int = 20) -> List[Dict]:
    """Retrieve the most recent training plans."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                sqlalchemy.text(
                    "SELECT id, naam, aangemaakt_op, plan_data FROM trainingsplannen "
                    "ORDER BY aangemaakt_op DESC LIMIT :limit"
                ),
                {"limit": limit}
            ).fetchall()
            return [
                {
                    "id": row[0],
                    "naam": row[1],
                    "aangemaakt_op": row[2],
                    **json.loads(row[3])
                }
                for row in rows
            ]
    except Exception as e:
        print(f"DB list error: {e}")
    return []


# Auto-initialize on import
try:
    init_db()
except Exception as e:
    print(f"DB init warning: {e}")
