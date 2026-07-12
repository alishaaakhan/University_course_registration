-- =====================================================================
-- University Course Registration System - MySQL Schema
-- Run this script first in MySQL Workbench / CLI to create the database.
--   mysql -u root -p < database/schema.sql
-- =====================================================================

DROP DATABASE IF EXISTS university_db;
CREATE DATABASE university_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE university_db;

-- ---------------------------------------------------------------------
-- Users table (application login / authentication)
-- ---------------------------------------------------------------------
CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'admin',
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Default admin login -> username: admin | password: admin123
-- (password_hash generated with werkzeug.security.generate_password_hash)
INSERT INTO users (username, password_hash, full_name, role) VALUES
('admin', 'scrypt:32768:8:1$PJn5vl4ZRspWw9qd$8b4016f309916d3057e1059cae0588bb6a4a4ce689664710d644bbb7d0f60d05c7e424f9373b452b6689a8d6dd188519657b186b35d8d655df49b3f3a67aa3a7', 'Registrar Admin', 'admin');

-- ---------------------------------------------------------------------
-- Department
-- ---------------------------------------------------------------------
CREATE TABLE department (
    dept_id    INT AUTO_INCREMENT PRIMARY KEY,
    dept_name  VARCHAR(100) NOT NULL UNIQUE,
    hod_name   VARCHAR(100),
    building   VARCHAR(50)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Student
-- ---------------------------------------------------------------------
CREATE TABLE student (
    student_id  INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    dept_id     INT,
    year        INT NOT NULL CHECK (year BETWEEN 1 AND 4),
    email       VARCHAR(100) UNIQUE,
    dob         DATE,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Faculty  (generalized entity; specialized via faculty_type)
-- ---------------------------------------------------------------------
CREATE TABLE faculty (
    faculty_id   INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    dept_id      INT,
    designation  VARCHAR(50),
    faculty_type ENUM('Permanent','Visiting') NOT NULL DEFAULT 'Permanent',
    FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE permanent_faculty (
    faculty_id      INT PRIMARY KEY,
    date_of_joining DATE,
    pay_scale       VARCHAR(30),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE visiting_faculty (
    faculty_id            INT PRIMARY KEY,
    contract_period        VARCHAR(30),
    honorarium_per_class    DECIMAL(8,2),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Course
-- ---------------------------------------------------------------------
CREATE TABLE course (
    course_id      VARCHAR(10) PRIMARY KEY,
    course_name    VARCHAR(120) NOT NULL,
    credits        INT NOT NULL,
    dept_id        INT,
    faculty_id     INT,
    seat_capacity  INT NOT NULL DEFAULT 60,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE SET NULL,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Enrollment (associative entity resolving Student <-> Course M:N)
-- ---------------------------------------------------------------------
CREATE TABLE enrollment (
    enroll_id    INT AUTO_INCREMENT PRIMARY KEY,
    student_id   INT NOT NULL,
    course_id    VARCHAR(10) NOT NULL,
    semester     VARCHAR(20) NOT NULL,
    grade        VARCHAR(3),
    enroll_date  DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_course_sem (student_id, course_id, semester)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Trigger: block INSERT into enrollment if the course is already full
-- ---------------------------------------------------------------------
DELIMITER $$
CREATE TRIGGER trg_check_seat_capacity
BEFORE INSERT ON enrollment
FOR EACH ROW
BEGIN
    DECLARE v_capacity INT;
    DECLARE v_enrolled  INT;

    SELECT seat_capacity INTO v_capacity FROM course WHERE course_id = NEW.course_id;
    SELECT COUNT(*) INTO v_enrolled FROM enrollment
        WHERE course_id = NEW.course_id AND semester = NEW.semester;

    IF v_enrolled >= v_capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Registration failed: course has no free seats left for this semester.';
    END IF;
END$$
DELIMITER ;

-- Helpful index for course-wise lookups used throughout the app
CREATE INDEX idx_enrollment_course ON enrollment(course_id);

-- ---------------------------------------------------------------------
-- Sample data
-- ---------------------------------------------------------------------
INSERT INTO department (dept_name, hod_name, building) VALUES
('Computer Science & Engineering', 'Dr. Kunal Mehta', 'Block A'),
('Electronics & Communication', 'Dr. Meera Iyengar', 'Block B'),
('Mechanical Engineering', 'Dr. Prakash Rao', 'Block C'),
('Civil Engineering', 'Dr. Neha Bhatt', 'Block D'),
('Mathematics & Sciences', 'Dr. S. Ganguly', 'Block E');

INSERT INTO student (name, dept_id, year, email, dob) VALUES
('Riya Sharma', 1, 3, 'riya.sharma@vidyapeeth.edu', '2004-06-15'),
('Aman Verma', 1, 3, 'aman.verma@vidyapeeth.edu', '2004-03-22'),
('Karthik Iyer', 1, 2, 'karthik.iyer@vidyapeeth.edu', '2005-11-09'),
('Farhan Sheikh', 1, 4, 'farhan.sheikh@vidyapeeth.edu', '2003-01-30'),
('Priya Nair', 2, 2, 'priya.nair@vidyapeeth.edu', '2005-08-12'),
('Divya Menon', 2, 3, 'divya.menon@vidyapeeth.edu', '2004-02-04'),
('Rohit Yadav', 3, 4, 'rohit.yadav@vidyapeeth.edu', '2003-05-19'),
('Sneha Kulkarni', 4, 3, 'sneha.kulkarni@vidyapeeth.edu', '2004-09-27');

INSERT INTO faculty (name, dept_id, designation, faculty_type) VALUES
('Dr. Kunal Mehta', 1, 'Professor', 'Permanent'),
('Ms. Sarah Thomas', 1, 'Guest Faculty', 'Visiting'),
('Dr. Meera Iyengar', 2, 'Associate Professor', 'Permanent'),
('Dr. Prakash Rao', 3, 'Professor', 'Permanent'),
('Dr. Neha Bhatt', 4, 'Assistant Professor', 'Permanent'),
('Mr. Vivek Sinha', 5, 'Guest Faculty', 'Visiting');

INSERT INTO permanent_faculty (faculty_id, date_of_joining, pay_scale) VALUES
(1, '2010-07-01', 'Level 14'),
(3, '2012-08-14', 'Level 13'),
(4, '2008-06-01', 'Level 14'),
(5, '2018-01-22', 'Level 12');

INSERT INTO visiting_faculty (faculty_id, contract_period, honorarium_per_class) VALUES
(2, 'Odd 2025-26', 1500.00),
(6, 'Odd 2025-26', 1200.00);

INSERT INTO course (course_id, course_name, credits, dept_id, faculty_id, seat_capacity) VALUES
('CS301', 'Database Management Systems', 4, 1, 1, 60),
('CS205', 'Data Structures & Algorithms', 4, 1, 1, 60),
('CS410', 'Compiler Design', 4, 1, 2, 40),
('EC110', 'Digital Electronics', 3, 2, 3, 50),
('MA204', 'Discrete Mathematics', 3, 5, 6, 80),
('ME150', 'Thermodynamics', 4, 3, 4, 55),
('CV220', 'Structural Analysis I', 3, 4, 5, 45),
('HU101', 'Technical Communication', 2, 5, 6, 60);

INSERT INTO enrollment (student_id, course_id, semester, grade, enroll_date) VALUES
(1, 'CS301', 'Odd 2025-26', NULL, '2025-07-20'),
(2, 'CS205', 'Odd 2025-26', 'A', '2025-07-20'),
(3, 'CS301', 'Odd 2025-26', NULL, '2025-07-21'),
(4, 'CS410', 'Odd 2025-26', NULL, '2025-07-21'),
(5, 'EC110', 'Odd 2025-26', NULL, '2025-07-22'),
(6, 'EC110', 'Even 2024-25', 'B+', '2025-01-15'),
(7, 'ME150', 'Odd 2025-26', NULL, '2025-07-22'),
(8, 'CV220', 'Odd 2025-26', NULL, '2025-07-23'),
(1, 'MA204', 'Even 2024-25', 'A', '2025-01-15'),
(2, 'MA204', 'Even 2024-25', 'A', '2025-01-15'),
(1, 'CS205', 'Even 2024-25', 'A', '2025-01-20');
