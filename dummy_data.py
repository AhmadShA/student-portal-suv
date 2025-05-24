from app import create_app
from models import db, Student, Course, Enrollment
from werkzeug.security import generate_password_hash
from datetime import datetime
import random
import warnings

# Suppress MySQL warnings
warnings.filterwarnings("ignore", message="Duplicate entry")

def create_dummy_students():
    students = [
        {"name": "Ali Ahmed", "email": "ali@example.com", "password": "password123"},
        {"name": "Sara Mohammed", "email": "sara@example.com", "password": "sara456"},
        {"name": "Omar Khalid", "email": "omar@example.com", "password": "omar789"},
    ]
    
    for student in students:
        if not Student.query.filter_by(email=student["email"]).first():
            new_student = Student(
                name=student["name"],
                email=student["email"],
                password_hash=generate_password_hash(student["password"])
            )
            db.session.add(new_student)
    db.session.commit()

def create_dummy_courses():
    courses = [
        {"title": "Mathematics", "description": "Basic algebra and calculus"},
        {"title": "Computer Science", "description": "Introduction to programming"},
        {"title": "Physics", "description": "Classical mechanics"},
    ]
    
    for course in courses:
        if not Course.query.filter_by(title=course["title"]).first():
            new_course = Course(
                title=course["title"],
                description=course["description"]
            )
            db.session.add(new_course)
    db.session.commit()

def create_dummy_enrollments():
    students = Student.query.all()
    courses = Course.query.all()
    
    for student in students:
        existing_courses = [e.course_id for e in student.enrollments]
        available_courses = [c for c in courses if c.id not in existing_courses]
        
        if available_courses:
            num_courses = random.randint(1, min(3, len(available_courses)))
            selected_courses = random.sample(available_courses, num_courses)
            
            for course in selected_courses:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    timestamp=datetime.utcnow()
                )
                db.session.add(enrollment)
    db.session.commit()

if __name__ == "__main__":
    # Create app instance and establish context
    app = create_app()
    
    with app.app_context():
        confirm = input("This will reset ALL data! Type 'YES' to continue: ")
        if confirm == 'YES':
            # Clean and recreate tables
            db.drop_all()
            db.create_all()
            
            # Generate dummy data
            create_dummy_students()
            create_dummy_courses()
            create_dummy_enrollments()
            
            print("✅ Dummy data created successfully!")
            print("Test users:")
            print("| Email             | Password    |")
            print("|-------------------|-------------|")
            print("| ali@example.com   | password123 |")
            print("| sara@example.com  | sara456     |")
            print("| omar@example.com  | omar789     |")
        else:
            print("Operation cancelled")