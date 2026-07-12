"""
routes/courses.py
-------------------
Full CRUD for the Course entity.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Course, Department, Faculty

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")


@courses_bp.route("/")
@login_required
def list_courses():
    """READ - list all courses with live seat usage."""
    courses = Course.query.order_by(Course.course_id).all()
    return render_template("courses/list.html", courses=courses)


@courses_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_course():
    """CREATE"""
    departments = Department.query.order_by(Department.dept_name).all()
    faculty_members = Faculty.query.order_by(Faculty.name).all()

    if request.method == "POST":
        try:
            course = Course(
                course_id=request.form["course_id"].strip().upper(),
                course_name=request.form["course_name"].strip(),
                credits=request.form.get("credits", type=int),
                dept_id=request.form.get("dept_id", type=int),
                faculty_id=request.form.get("faculty_id", type=int) or None,
                seat_capacity=request.form.get("seat_capacity", type=int) or 60,
            )
            db.session.add(course)
            db.session.commit()
            flash(f"Course '{course.course_id}' added successfully.", "success")
            return redirect(url_for("courses.list_courses"))
        except IntegrityError:
            db.session.rollback()
            flash("Could not add course — that Course ID already exists.", "danger")

    return render_template(
        "courses/form.html", course=None, departments=departments, faculty_members=faculty_members
    )


@courses_bp.route("/edit/<course_id>", methods=["GET", "POST"])
@login_required
def edit_course(course_id):
    """UPDATE"""
    course = Course.query.get_or_404(course_id)
    departments = Department.query.order_by(Department.dept_name).all()
    faculty_members = Faculty.query.order_by(Faculty.name).all()

    if request.method == "POST":
        course.course_name = request.form["course_name"].strip()
        course.credits = request.form.get("credits", type=int)
        course.dept_id = request.form.get("dept_id", type=int)
        course.faculty_id = request.form.get("faculty_id", type=int) or None
        course.seat_capacity = request.form.get("seat_capacity", type=int) or 60
        db.session.commit()
        flash(f"Course '{course.course_id}' updated successfully.", "success")
        return redirect(url_for("courses.list_courses"))

    return render_template(
        "courses/form.html", course=course, departments=departments, faculty_members=faculty_members
    )


@courses_bp.route("/delete/<course_id>", methods=["POST"])
@login_required
def delete_course(course_id):
    """DELETE"""
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash(f"Course '{course_id}' deleted.", "info")
    return redirect(url_for("courses.list_courses"))
