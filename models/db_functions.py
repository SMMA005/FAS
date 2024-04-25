
from datetime import datetime
from .models import User, Attendance
from . import db
from datetime import datetime, timedelta

def get_student_details(student_id):
    student = User.query.filter_by(id=student_id).first()
    if student:
        return {
            'id': student.id,
            'student_number': student.student_number,
            'surname': student.surname,
            'other_names': student.other_names,
            'mobile_no': student.mobile_no,
            'address': student.address,
            'course': student.course,
            'date_enrolled': student.date_enrolled
        }
    return None

# def check_and_create_attendance(student_id, db):
#     today = datetime.today().date()
#     attendance = Attendance.query.filter_by(user_id=student_id, date_time=datetime.now().date()).first()
    
#     if not attendance:
#         new_attendance = Attendance(
#             user_id=student_id,
#             date_time=datetime.now()
#         )
#         db.session.add(new_attendance)
#         db.session.commit()
#         return f"Attendance recorded for student ID: {student_id}", True
#     return "Student already marked present today", False

def check_and_create_attendance(student_id, db):
    try:
        # Get today's date and the date 24 hours ago
        today = datetime.today().date()
        twenty_four_hours_ago = datetime.now() - timedelta(hours=2)

        # Check if the student has any attendance records within the last 24 hours
        attendance_within_24_hours = Attendance.query.filter(
            Attendance.user_id == student_id,
            Attendance.date_time >= twenty_four_hours_ago
        ).first()

        if attendance_within_24_hours:
            # If the student has already been marked present within the last 24 hours, return appropriate message
            return "User has already been marked present within the last 2 hours", False

        # Check if the student has already been marked present today
        attendance_today = Attendance.query.filter_by(user_id=student_id, date_time=today).first()

        if not attendance_today:
            # If the student has not been marked present today, create a new attendance record
            new_attendance = Attendance(
                user_id=student_id,
                date_time=datetime.now()
            )
            db.session.add(new_attendance)
            db.session.commit()
            return f"Attendance recorded for student ID: {student_id}", True
        else:
            # If the student has already been marked present today, return appropriate message
            return "User already marked present today", False

    except Exception as e:
        # Rollback the session in case of an error and return error message
        db.session.rollback()
        return f"Error recording attendance: {str(e)}", False