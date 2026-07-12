"""
routes/enrollment.py
----------------------
Create / list / delete student course-registrations. Seat-capacity is
enforced twice: once here (for a fast, friendly error message) and again
by the trg_check_seat_capacity trigger in MySQL itself (the authoritative,
race-condition-safe guarantee — see database/schema.sql).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError, OperationalError

from extensions import db
from models import Enrollment, Student, Course

enrollment_bp = Blueprint("enrollment", __name__, url_prefix="/enrollment")


@enrollment_bp.route("/")
@login_required
def list_enrollments():
    """READ - most recent registrations first."""
    enrollments = Enrollment.query.order_by(Enrollment.enroll_id.desc()).all()
    return render_template("enrollment/list.html", enrollments=enrollments)


@enrollment_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_enrollment():
    """CREATE - register a student into a course for a given semester."""
    students = Student.query.order_by(Student.name).all()
    courses = Course.query.order_by(Course.course_id).all()

    if request.method == "POST":
        student_id = request.form.get("student_id", type=int)
        course_id = request.form["course_id"]
        semester = request.form["semester"].strip()
        grade = request.form.get("grade", "").strip() or None

        course = Course.query.get_or_404(course_id)

        # Friendly, app-level seat check (the DB trigger is the real guarantee)
        if course.is_full(semester):
            flash(
                f"Registration blocked: '{course.course_name}' has no free seats "
                f"left for {semester}.",
                "danger",
            )
            return render_template(
                "enrollment/form.html", students=students, courses=courses
            )

        try:
            enrollment = Enrollment(
                student_id=student_id,
                course_id=course_id,
                semester=semester,
                grade=grade,
            )
            db.session.add(enrollment)
            db.session.commit()
            flash("Student enrolled successfully.", "success")
            return redirect(url_for("enrollment.list_enrollments"))
        except IntegrityError:
            db.session.rollback()
            flash("This student is already registered for that course & semester.", "danger")
        except OperationalError as exc:
            # Raised by the MySQL trigger (SIGNAL SQLSTATE '45000') if the
            # seat-capacity check somehow still fails at the database layer
            # (e.g. a race with another concurrent registration).
            db.session.rollback()
            flash(f"Registration rejected by the database: {exc.orig}", "danger")

    return render_template("enrollment/form.html", students=students, courses=courses)


@enrollment_bp.route("/delete/<int:enroll_id>", methods=["POST"])
@login_required
def delete_enrollment(enroll_id):
    """DELETE"""
    enrollment = Enrollment.query.get_or_404(enroll_id)
    db.session.delete(enrollment)
    db.session.commit()
    flash("Enrollment record removed.", "info")
    return redirect(url_for("enrollment.list_enrollments"))
