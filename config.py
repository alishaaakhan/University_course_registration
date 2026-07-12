"""
config.py
---------
Central configuration for the Flask app. Values are read from environment
variables (loaded from a .env file via python-dotenv) so credentials are
never hard-coded into source control.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # populate os.environ from a .env file if present


class Config:
    """Base configuration shared by the whole application."""

    # Used by Flask to sign session cookies / CSRF tokens
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # ---- MySQL connection settings ----
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "university_db")

    # SQLAlchemy connects to MySQL through the PyMySQL driver
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # avoids "MySQL server has gone away" errors
        "pool_recycle": 280,
    }
