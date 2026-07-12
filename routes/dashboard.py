"""
routes/dashboard.py
--------------------
Registrar landing page: KPI cards + department-wise enrollment summary.
"""

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from extensions import db
from models import Student, Course, Faculty, Department, Enrollment

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    total_students = Student.query.count()
    total_courses = Course.query.count()
    total_faculty = Faculty.query.count()
    total_enrollments = Enrollment.query.count()

    permanent_count = Faculty.query.filter_by(faculty_type="Permanent").count()
    visiting_count = Faculty.query.filter_by(faculty_type="Visiting").count()

    # Department-wise student & course counts (single aggregate query)
    dept_stats = (
        db.session.query(
            Department.dept_name,
            func.count(func.distinct(Student.student_id)).label("student_count"),
        )
        .outerjoin(Student, Student.dept_id == Department.dept_id)
        .group_by(Department.dept_id, Department.dept_name)
        .order_by(func.count(func.distinct(Student.student_id)).desc())
        .all()
    )

    recent_enrollments = (
        Enrollment.query.order_by(Enrollment.enroll_id.desc()).limit(6).all()
    )

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_courses=total_courses,
        total_faculty=total_faculty,
        total_enrollments=total_enrollments,
        permanent_count=permanent_count,
        visiting_count=visiting_count,
        dept_stats=dept_stats,
        recent_enrollments=recent_enrollments,
    )
