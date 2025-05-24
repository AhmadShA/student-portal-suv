CREATE DATABASE IF NOT EXISTS student_portal;
USE student_portal;

CREATE TABLE student (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Added AUTO_INCREMENT
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255)
);

CREATE TABLE course (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Added AUTO_INCREMENT
    title VARCHAR(100),
    description TEXT
);

CREATE TABLE enrollment (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- Added AUTO_INCREMENT
    student_id INT,
    course_id INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE
);