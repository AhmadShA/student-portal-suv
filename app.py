from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import humanize
from models import db  # Import db from models

# Initialize extensions
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:0000@localhost/student_portal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Import models AFTER db initialization
    with app.app_context():
        from models import Student, Course, Enrollment
        db.create_all()

    # Custom Jinja Filters
    @app.template_filter('time_ago')
    def time_ago(dt):
        return humanize.naturaltime(datetime.now() - dt)

    # Routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            try:
                name = request.form['name']
                email = request.form['email']
                password = generate_password_hash(request.form['password'])
                
                if Student.query.filter_by(email=email).first():
                    return render_template('register.html', error="Email already exists!")
                
                new_student = Student(name=name, email=email, password_hash=password)
                db.session.add(new_student)
                db.session.commit()
                return redirect(url_for('login'))
            
            except Exception as e:
                db.session.rollback()
                return render_template('register.html', error=str(e))
    
        # GET request - no manual CSRF generation needed
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            try:
                email = request.form['email']
                password = request.form['password']
                student = Student.query.filter_by(email=email).first()
                
                if student and check_password_hash(student.password_hash, password):
                    session['user_id'] = student.id
                    return redirect(url_for('dashboard'))
                
                return render_template('login.html', error="Invalid credentials!")
            
            except Exception as e:
                return render_template('login.html', error=str(e))
        
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        try:
            student = Student.query.get(session['user_id'])
            enrollments = Enrollment.query.filter_by(student_id=student.id).all()
            courses = [enrollment.course for enrollment in enrollments]
            return render_template('dashboard.html', student=student, courses=courses)
        
        except Exception as e:
            # Fallback if error.html is missing
            return f"An error occurred: {str(e)}", 500

    @app.route('/courses')
    def courses():
        return render_template('courses.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('index'))

    # API Endpoints
    @app.route('/api/courses')
    def api_courses():
        try:
            courses = Course.query.all()
            return jsonify([{'id': c.id, 'title': c.title, 'description': c.description} for c in courses])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/ajax/enroll', methods=['POST'])
    def ajax_enroll():
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        try:
            # Get JSON data
            data = request.get_json()
            if not data or 'course_id' not in data:
                return jsonify({'success': False, 'error': 'Invalid request data'}), 400

            course_id = data['course_id']
            student_id = session['user_id']

            # Check if course exists
            course = Course.query.get(course_id)
            if not course:
                return jsonify({'success': False, 'error': 'Course not found'}), 404

            # Check existing enrollment
            existing = Enrollment.query.filter_by(
                student_id=student_id,
                course_id=course_id
            ).first()

            if existing:
                return jsonify({'success': False, 'error': 'Already enrolled'}), 409

            # Create new enrollment
            enrollment = Enrollment(
                student_id=student_id,
                course_id=course_id
            )
            db.session.add(enrollment)
            db.session.commit()

            return jsonify({'success': True})

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Enrollment error: {str(e)}")
            return jsonify({'success': False, 'error': 'Database error'}), 500

    @app.route('/ajax/leave', methods=['POST'])
    def ajax_leave():
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        try:
            student_id = session['user_id']
            course_id = request.json.get('course_id')
            
            if not course_id:
                return jsonify({'success': False, 'error': 'Missing course ID'}), 400

            # Find the enrollment
            enrollment = Enrollment.query.filter_by(
                student_id=student_id,
                course_id=course_id
            ).first()

            if not enrollment:
                return jsonify({'success': False, 'error': 'Enrollment not found'}), 404

            db.session.delete(enrollment)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Successfully left course'})
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error leaving course: {str(e)}")
            return jsonify({'success': False, 'error': 'Database error'}), 500
    
    return app

# Create application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)