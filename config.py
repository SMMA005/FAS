class Config:
    # SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://username:password@localhost/dbname'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:8080/attendanceai'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'