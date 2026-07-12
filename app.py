"""
app.py
------
Application factory + entry point.
Run with:  python app.py
The dev server starts on http://127.0.0.1:5000
"""

from flask import Flask, render_template, redirect, url_for
from flask_login import login_required

from config import Config
from extensions import db, login_manager
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---- initialise extensions ----
    db.init_app(app)
    login_manager.init_app(app)

    # ---- register blueprints ----
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.students import students_bp
    from routes.courses import courses_bp
    from routes.faculty import faculty_bp
    from routes.departments import departments_bp
    from routes.enrollment import enrollment_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(enrollment_bp)

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.dashboard"))

    # ---- error handlers ----
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login calls this on every request to reload the logged-in user."""
    return db.session.get(User, int(user_id))


if __name__ == "__main__":
    # debug=True enables auto-reload + the interactive debugger for development.
    # Turn this off (or set FLASK_DEBUG=0) before deploying anywhere public.
    app.run(debug=True)
