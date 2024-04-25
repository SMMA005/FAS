from flask import Blueprint, request, render_template, redirect, url_for, flash,jsonify
from app.models.models import db, User, Attendance
from app.facial_rec.enocoding_generator import main_encoding
import base64
from PIL import Image
import io
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import os
admin_blueprint = Blueprint('admin', __name__)

@admin_blueprint.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@admin_blueprint.route('/add_student_page', methods=['GET', 'POST'])
def add_student_page():
    return render_template('add_user.html')

@admin_blueprint.route('/add_student', methods=['GET', 'POST'])
def add_student():
    # Check if the request method is POST
    if request.method == 'POST':
        file = request.files.get('userImage')  # Use .get() to avoid KeyError if 'userImage' not provided
        student_number = request.form.get('studentNumber')
        surname = request.form.get('surname')
        other_names = request.form.get('otherNames')
        mobile_no = request.form.get('mobileNo')
        address = request.form.get('address')
        course = request.form.get('course')
        date_enrolled = request.form.get('dateEnrolled')

        # Check if all required form data is provided
        if not all([file, student_number, surname, other_names, mobile_no, address, course, date_enrolled]):
            flash('Missing data in form submission', 'error')
            return redirect(url_for('add_student'))  # Adjust to your correct form route

        # Proceed if the file exists and is of an allowed type
        if file and allowed_file(file.filename):
            # Create the user to get an ID
            new_user = User(
                student_number=student_number,
                surname=surname,
                other_names=other_names,
                mobile_no=mobile_no,
                address=address,
                course=course,
                date_enrolled=datetime.strptime(date_enrolled, '%Y-%m-%d')
            )
            try:
                db.session.add(new_user)
                db.session.commit()
            except:
                flash('There was a problem pushing your  information into the database!', 'error')
                db.session.rollback()
                return redirect(url_for('admin.add_student_page'))

           
            # Save the file using the new user's ID
            filename = secure_filename(f"{new_user.id}.png")  # Ensuring the file extension is correct
            save_path = os.path.join("C:/xampp/htdocs/AI FACE/attendanceAppFlask/attendanceAppFlask/app/static/img/Users", filename)
            file.save(save_path)
            
            flash('Student added successfully!', 'success')
            main_encoding()
            return redirect(url_for('admin.add_student_page'))  # Redirect after successful addition

        else:
            flash('Invalid file type or missing image.', 'error')
            return redirect(url_for('admin.add_student_page'))

    # If not a POST request or other unspecified issues
    return jsonify({'error': 'Unsupported request method or missing data'}), 400

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@admin_blueprint.route('/search_user')
def search_user():
    query = request.args.get('query', '').strip()
    if query:
        # Search query is not empty, filter users based on the input
        users = User.query.filter(
            db.or_(
                User.surname.ilike(f'%{query}%'),
                User.other_names.ilike(f'%{query}%'),
                User.course.ilike(f'%{query}%'),
                User.student_number.ilike(f'%{query}%'),
                User.mobile_no.ilike(f'%{query}%'),
                User.address.ilike(f'%{query}%')
            )
        ).all()
    else:
        # If no query, return all users
        users = User.query.all()

    # Create a list of dicts, each dict containing user data including all details to be displayed
    user_data = [
        {
            'id': user.id,
            'student_number': user.student_number,
            'surname': user.surname,
            'other_names': user.other_names,
            'mobile_no': user.mobile_no,
            'address': user.address,
            'course': user.course,
            'date_enrolled': user.date_enrolled.strftime('%Y-%m-%d')  # Formatting the date
        }
        for user in users
    ]
    return jsonify(user_data)
@admin_blueprint.route('/search_user_page', methods=['GET', 'POST'])
def search_user_page():
    return render_template('search_user.html') 
@admin_blueprint.route('/user_details/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    user = User.query.get(user_id)
    if user:
        user_data = {
            'student_number': user.student_number,
            'surname': user.surname,
            'other_names': user.other_names,
            'mobile_no': user.mobile_no,
            'address': user.address,
            'course': user.course,
            'date_enrolled': user.date_enrolled.strftime('%Y-%m-%d')  # Ensure the date format matches the frontend expectation
        }
        return jsonify(user_data)
    return jsonify({'error': 'User not found'}), 404
@admin_blueprint.route('/update_user', methods=['POST'])
def update_user():
    user_id = request.form['user_id']
    user = User.query.get(user_id)
    if user:
        user.student_number = request.form['student_number']
        user.surname = request.form['surname']
        user.other_names = request.form['other_names']
        user.mobile_no = request.form['mobile_no']
        user.address = request.form['address']
        user.course = request.form['course']
        user.date_enrolled = datetime.strptime(request.form['date_enrolled'], '%Y-%m-%d')  # Parsing the date string to a date object
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    return jsonify({'error': 'User not found'}), 404
@admin_blueprint.route('/edit_user_page', methods=['GET', 'POST'])
def edit_user_page():

    return render_template('edit_user.html')
@admin_blueprint.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        Attendance.query.filter_by(user_id=user_id).delete()

        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User and related attendance records deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user and related records: ' + str(e)}), 500
@admin_blueprint.route('/view_attendance')
def view_attendance():
  
    return render_template('view_attendance.html')

@admin_blueprint.route('/search_attendance')
def search_attendance():
    query = request.args.get('query', '').strip()
    if query:
        # Filter by user's name, surname, or date/time of attendance
        attendances = Attendance.query.join(User).filter(
            db.or_(
                User.surname.ilike(f'%{query}%'),
                User.other_names.ilike(f'%{query}%'),
                User.student_number.ilike(f'%{query}%'),  # If you want to search by student number
                Attendance.date_time.ilike(f'%{query}%')
            )
        ).all()
    else:
        # If no query, return all attendance records
        attendances = Attendance.query.join(User).all()

    # Serialize data
    attendance_data = [
        {
            'id': attendance.id,
            'user_name': f"{attendance.user.surname}, {attendance.user.other_names}",
            'date_time': attendance.date_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        for attendance in attendances
    ]
    return jsonify(attendance_data)
@admin_blueprint.route('/logout')
def logout():
    
    return ""