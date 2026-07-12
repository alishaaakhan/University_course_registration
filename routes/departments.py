"""
routes/departments.py
-----------------------
Full CRUD for the Department entity.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Department

departments_bp = Blueprint("departments", __name__, url_prefix="/departments")


@departments_bp.route("/")
@login_required
def list_departments():
    """READ"""
    departments = Department.query.order_by(Department.dept_name).all()
    return render_template("departments/list.html", departments=departments)


@departments_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_department():
    """CREATE"""
    if request.method == "POST":
        try:
            dept = Department(
                dept_name=request.form["dept_name"].strip(),
                hod_name=request.form.get("hod_name", "").strip() or None,
                building=request.form.get("building", "").strip() or None,
            )
            db.session.add(dept)
            db.session.commit()
            flash(f"Department '{dept.dept_name}' added successfully.", "success")
            return redirect(url_for("departments.list_departments"))
        except IntegrityError:
            db.session.rollback()
            flash("Could not add department — that name already exists.", "danger")

    return render_template("departments/form.html", department=None)


@departments_bp.route("/edit/<int:dept_id>", methods=["GET", "POST"])
@login_required
def edit_department(dept_id):
    """UPDATE"""
    department = Department.query.get_or_404(dept_id)

    if request.method == "POST":
        department.dept_name = request.form["dept_name"].strip()
        department.hod_name = request.form.get("hod_name", "").strip() or None
        department.building = request.form.get("building", "").strip() or None
        db.session.commit()
        flash(f"Department '{department.dept_name}' updated successfully.", "success")
        return redirect(url_for("departments.list_departments"))

    return render_template("departments/form.html", department=department)


@departments_bp.route("/delete/<int:dept_id>", methods=["POST"])
@login_required
def delete_department(dept_id):
    """DELETE"""
    department = Department.query.get_or_404(dept_id)

    if department.students or department.courses:
        flash(
            f"Cannot delete '{department.dept_name}' — it still has students or courses assigned.",
            "danger",
        )
        return redirect(url_for("departments.list_departments"))

    db.session.delete(department)
    db.session.commit()
    flash(f"Department '{department.dept_name}' deleted.", "info")
    return redirect(url_for("departments.list_departments"))
