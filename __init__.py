from flask import *
from .views.admin import admin_blueprint
# from .views.facial_auth import facial_auth_blueprint
from .models import db
from .models.db_functions import get_student_details, check_and_create_attendance
from .models.models import User, Attendance
from flask_sqlalchemy import SQLAlchemy
import datetime
import cv2
import face_recognition
import time
from concurrent.futures import ThreadPoolExecutor
import cvzone  # Ensure this is installed via pip
from app.models.models import db, User, Attendance
import pickle
import numpy as np
from threading import Thread, Event

background_thread = None
stop_thread = Event()



def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/attendanceai'
    app.config['UPLOAD_FOLDER'] = 'static/img/Users'

    app.secret_key = 'your_secret_key'

    db.init_app(app)

    with app.app_context():
        db.create_all()
   
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    @app.route('/detect')
    def detection():
 
        global background_thread, stop_thread
        session['face_detection'] = True
        if background_thread is None or not background_thread.is_alive():
            stop_thread.clear()
            background_thread = Thread(target=start_face_detection, args=(app,stop_thread))
            background_thread.start()
        return redirect(url_for('admin.home'))

    @app.route('/stop-face-detection')
    def stop_face_detection():
        global stop_thread
        session['face_detection'] = False
        stop_thread.set()
        return redirect(url_for('admin.home'))

    @app.route('/')
    def index():
        return render_template('index.html')

    def process_face(faceLoc, encodeFace):
        file = open('C:/xampp/htdocs/AI FACE/attendanceAppFlask/attendanceAppFlask/app/facial_rec/encodings.pickle', 'rb')
        encodelistwithids = pickle.load(file)
        file.close()
        encodeKnownList, studentIds = encodelistwithids
        matches = face_recognition.compare_faces(encodeKnownList, encodeFace)
        face_distance = face_recognition.face_distance(encodeKnownList, encodeFace)
        match_index = np.argmin(face_distance)
        
        if matches[match_index]:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = x1, y1, x2 - x1, y2 - y1
            text = f"Face Detected = id:{studentIds[match_index]}"
            return studentIds[match_index],True, bbox, text
        return None,False, None, None

    def start_face_detection(app, stop_event):
        with app.app_context():
            video_capture = cv2.VideoCapture(0)
            video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            last_query_time = 0  
            interval_between_queries = 5  

            image_registry = {}  

            while True:
                is_frame_captured, frame = video_capture.read()
                reduced_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                reduced_frame = cv2.cvtColor(reduced_frame, cv2.COLOR_BGR2RGB)
                detected_faces = face_recognition.face_locations(reduced_frame)
                face_encodings = face_recognition.face_encodings(reduced_frame, detected_faces)

                for location, encoding in zip(detected_faces, face_encodings):
                    person_id, is_detected, bounding_box, display_text = process_face(location, encoding)

                    if is_detected and bounding_box and person_id is not None:
                        current_time = time.time()
                        if current_time - last_query_time > interval_between_queries:
                            last_query_time = current_time

                            student_info = get_student_details(person_id)
                            display_text, attendance_logged = check_and_create_attendance(person_id, db)
                            print(display_text, attendance_logged)
                            if attendance_logged and person_id not in image_registry:
                                extracted_face = frame[bounding_box[1]:bounding_box[1]+bounding_box[3], bounding_box[0]:bounding_box[0]+bounding_box[2]]
                                timestamp = time.strftime("%Y%m%d-%H%M%S")
                                filename = f"C:/xampp/htdocs/AI FACE/attendanceAppFlask/attendanceAppFlask/app/static/img/Temp/{person_id}_{timestamp}.jpg"
                                cv2.imwrite(filename, extracted_face)
                                print(f"Face captured and saved to {filename}")
                                image_registry[person_id] = filename

                            frame = cvzone.cornerRect(frame, bounding_box, rt=1)
                            cv2.putText(frame, display_text, (bounding_box[0], bounding_box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                cv2.imshow("Face Recognition", frame)
                if cv2.waitKey(1) & 0xFF == ord('q') or stop_thread.is_set():
                    break

            video_capture.release()
            cv2.destroyAllWindows()
    # def test_db():
    #     new_user = User(
    #         student_number="202401",
    #         surname="Doe",
    #         other_names="John",
    #         mobile_no="1234567890",
    #         address="1234 Elm Street",
    #         course="Biology",
    #         date_enrolled=datetime.date.today()
    #     )

    #     # Adding the new user to the session
    #     db.session.add(new_user)
    #     db.session.commit()

    #     # Creating a new attendance record for this user
    #     new_attendance = Attendance(
    #         user_id=new_user.id,  # This links the attendance to the user
    #         date_time=datetime.datetime.now()
    #     )

    #     # Adding the new attendance record to the session
    #     db.session.add(new_attendance)
    #     db.session.commit()
    #     try:
    #         user = User.query.first()
    #         return 'Database Connected! First user surname: '
    #     except Exception as e:
    #         return 'Failed to connect to the database: ' + str(e)
    return app
