"""
extensions.py
-------------
Extension objects are created here, unbound, and initialised on the app
inside app.py via `.init_app()`. Keeping them in a separate module lets
every blueprint import `db` / `login_manager` without circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"
