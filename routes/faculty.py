"""
routes/faculty.py
-------------------
Full CRUD for the Faculty entity, including its Permanent/Visiting
specialization sub-tables.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models import Faculty, Department, PermanentFaculty, VisitingFaculty

faculty_bp = Blueprint("faculty", __name__, url_prefix="/faculty")


@faculty_bp.route("/")
@login_required
def list_faculty():
    """READ - list all faculty with their specialization type."""
    faculty_members = Faculty.query.order_by(Faculty.name).all()
    return render_template("faculty/list.html", faculty_members=faculty_members)


@faculty_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_faculty():
    """CREATE - also creates the matching Permanent/Visiting subtype row."""
    departments = Department.query.order_by(Department.dept_name).all()

    if request.method == "POST":
        faculty_type = request.form["faculty_type"]

        faculty = Faculty(
            name=request.form["name"].strip(),
            dept_id=request.form.get("dept_id", type=int),
            designation=request.form.get("designation", "").strip(),
            faculty_type=faculty_type,
        )
        db.session.add(faculty)
        db.session.flush()  # get faculty.faculty_id before commit

        if faculty_type == "Permanent":
            db.session.add(PermanentFaculty(
                faculty_id=faculty.faculty_id,
                date_of_joining=request.form.get("date_of_joining") or None,
                pay_scale=request.form.get("pay_scale", "").strip() or None,
            ))
        else:  # Visiting
            db.session.add(VisitingFaculty(
                faculty_id=faculty.faculty_id,
                contract_period=request.form.get("contract_period", "").strip() or None,
                honorarium_per_class=request.form.get("honorarium_per_class", type=float) or None,
            ))

        db.session.commit()
        flash(f"Faculty '{faculty.name}' added successfully.", "success")
        return redirect(url_for("faculty.list_faculty"))

    return render_template("faculty/form.html", faculty=None, departments=departments)


@faculty_bp.route("/edit/<int:faculty_id>", methods=["GET", "POST"])
@login_required
def edit_faculty(faculty_id):
    """UPDATE"""
    faculty = Faculty.query.get_or_404(faculty_id)
    departments = Department.query.order_by(Department.dept_name).all()

    if request.method == "POST":
        faculty.name = request.form["name"].strip()
        faculty.dept_id = request.form.get("dept_id", type=int)
        faculty.designation = request.form.get("designation", "").strip()
        new_type = request.form["faculty_type"]

        # If the specialization type changed, drop the old subtype row
        # and create the new one so exactly one subtype row ever exists.
        if new_type != faculty.faculty_type:
            if faculty.permanent_detail:
                db.session.delete(faculty.permanent_detail)
            if faculty.visiting_detail:
                db.session.delete(faculty.visiting_detail)
            faculty.faculty_type = new_type
            db.session.flush()

        if new_type == "Permanent":
            detail = faculty.permanent_detail or PermanentFaculty(faculty_id=faculty.faculty_id)
            detail.date_of_joining = request.form.get("date_of_joining") or None
            detail.pay_scale = request.form.get("pay_scale", "").strip() or None
            db.session.add(detail)
        else:
            detail = faculty.visiting_detail or VisitingFaculty(faculty_id=faculty.faculty_id)
            detail.contract_period = request.form.get("contract_period", "").strip() or None
            detail.honorarium_per_class = request.form.get("honorarium_per_class", type=float) or None
            db.session.add(detail)

        db.session.commit()
        flash(f"Faculty '{faculty.name}' updated successfully.", "success")
        return redirect(url_for("faculty.list_faculty"))

    return render_template("faculty/form.html", faculty=faculty, departments=departments)


@faculty_bp.route("/delete/<int:faculty_id>", methods=["POST"])
@login_required
def delete_faculty(faculty_id):
    """DELETE"""
    faculty = Faculty.query.get_or_404(faculty_id)
    db.session.delete(faculty)
    db.session.commit()
    flash(f"Faculty '{faculty.name}' deleted.", "info")
    return redirect(url_for("faculty.list_faculty"))
