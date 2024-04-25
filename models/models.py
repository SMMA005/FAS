from . import db
import datetime

class User(db.Model):
    __tablename__ = 'user' 
    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(50), unique=True, nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    other_names = db.Column(db.String(100), nullable=False)
    mobile_no = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    date_enrolled = db.Column(db.Date, default=datetime.date.today, nullable=False)

    attendances = db.relationship('Attendance', backref='user', lazy=True)

class Attendance(db.Model):
    __tablename__ = 'attendance'  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
