"""
routes/students.py
--------------------
Full CRUD for the Student entity.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Student, Department

students_bp = Blueprint("students", __name__, url_prefix="/students")


@students_bp.route("/")
@login_required
def list_students():
    """READ - list all students, optionally filtered by department."""
    dept_filter = request.args.get("dept_id", type=int)

    query = Student.query
    if dept_filter:
        query = query.filter_by(dept_id=dept_filter)

    students = query.order_by(Student.name).all()
    departments = Department.query.order_by(Department.dept_name).all()

    return render_template(
        "students/list.html",
        students=students,
        departments=departments,
        selected_dept=dept_filter,
    )


@students_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_student():
    """CREATE"""
    departments = Department.query.order_by(Department.dept_name).all()

    if request.method == "POST":
        try:
            student = Student(
                name=request.form["name"].strip(),
                dept_id=request.form.get("dept_id", type=int),
                year=request.form.get("year", type=int),
                email=request.form.get("email", "").strip() or None,
                dob=request.form.get("dob") or None,
            )
            db.session.add(student)
            db.session.commit()
            flash(f"Student '{student.name}' added successfully.", "success")
            return redirect(url_for("students.list_students"))
        except IntegrityError:
            db.session.rollback()
            flash("Could not add student — email may already be in use.", "danger")

    return render_template("students/form.html", student=None, departments=departments)


@students_bp.route("/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    """UPDATE"""
    student = Student.query.get_or_404(student_id)
    departments = Department.query.order_by(Department.dept_name).all()

    if request.method == "POST":
        try:
            student.name = request.form["name"].strip()
            student.dept_id = request.form.get("dept_id", type=int)
            student.year = request.form.get("year", type=int)
            student.email = request.form.get("email", "").strip() or None
            student.dob = request.form.get("dob") or None
            db.session.commit()
            flash(f"Student '{student.name}' updated successfully.", "success")
            return redirect(url_for("students.list_students"))
        except IntegrityError:
            db.session.rollback()
            flash("Could not update student — email may already be in use.", "danger")

    return render_template("students/form.html", student=student, departments=departments)


@students_bp.route("/delete/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):
    """DELETE"""
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f"Student '{student.name}' deleted.", "info")
    return redirect(url_for("students.list_students"))
