"""
models.py
---------
SQLAlchemy ORM models. Table/column names match database/schema.sql
exactly so the same MySQL database can be created either by running the
raw SQL script or by calling db.create_all() from this file.
"""

from datetime import date
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    """Application login account (registrar / admin staff)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="admin")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def check_password(self, plain_password: str) -> bool:
        return check_password_hash(self.password_hash, plain_password)


class Department(db.Model):
    __tablename__ = "department"

    dept_id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(100), nullable=False, unique=True)
    hod_name = db.Column(db.String(100))
    building = db.Column(db.String(50))

    students = db.relationship("Student", backref="department", lazy=True)
    faculty_members = db.relationship("Faculty", backref="department", lazy=True)
    courses = db.relationship("Course", backref="department", lazy=True)

    @property
    def student_count(self):
        return len(self.students)

    @property
    def course_count(self):
        return len(self.courses)


class Student(db.Model):
    __tablename__ = "student"

    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey("department.dept_id", ondelete="SET NULL"))
    year = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), unique=True)
    dob = db.Column(db.Date)

    enrollments = db.relationship(
        "Enrollment", backref="student", lazy=True, cascade="all, delete-orphan"
    )


class Faculty(db.Model):
    __tablename__ = "faculty"

    faculty_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey("department.dept_id", ondelete="SET NULL"))
    designation = db.Column(db.String(50))
    faculty_type = db.Column(db.Enum("Permanent", "Visiting", name="faculty_type_enum"),
                              nullable=False, default="Permanent")

    courses = db.relationship("Course", backref="faculty", lazy=True)
    permanent_detail = db.relationship(
        "PermanentFaculty", backref="faculty", uselist=False, cascade="all, delete-orphan"
    )
    visiting_detail = db.relationship(
        "VisitingFaculty", backref="faculty", uselist=False, cascade="all, delete-orphan"
    )


class PermanentFaculty(db.Model):
    __tablename__ = "permanent_faculty"

    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.faculty_id", ondelete="CASCADE"),
                            primary_key=True)
    date_of_joining = db.Column(db.Date)
    pay_scale = db.Column(db.String(30))


class VisitingFaculty(db.Model):
    __tablename__ = "visiting_faculty"

    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.faculty_id", ondelete="CASCADE"),
                            primary_key=True)
    contract_period = db.Column(db.String(30))
    honorarium_per_class = db.Column(db.Numeric(8, 2))


class Course(db.Model):
    __tablename__ = "course"

    course_id = db.Column(db.String(10), primary_key=True)
    course_name = db.Column(db.String(120), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey("department.dept_id", ondelete="SET NULL"))
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.faculty_id", ondelete="SET NULL"))
    seat_capacity = db.Column(db.Integer, nullable=False, default=60)

    enrollments = db.relationship(
        "Enrollment", backref="course", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def enrolled_count(self):
        """Number of students currently enrolled (any semester)."""
        return len(self.enrollments)

    def seats_left(self, semester: str) -> int:
        taken = Enrollment.query.filter_by(course_id=self.course_id, semester=semester).count()
        return self.seat_capacity - taken

    def is_full(self, semester: str) -> bool:
        return self.seats_left(semester) <= 0


class Enrollment(db.Model):
    __tablename__ = "enrollment"

    enroll_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.student_id", ondelete="CASCADE"),
                            nullable=False)
    course_id = db.Column(db.String(10), db.ForeignKey("course.course_id", ondelete="CASCADE"),
                           nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    grade = db.Column(db.String(3))
    enroll_date = db.Column(db.Date, default=date.today)

    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", "semester", name="uq_student_course_sem"),
    )
