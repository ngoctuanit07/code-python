# config.py

import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/quan_ly_kho'  # Thay 'username' và 'password'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Giới hạn 16MB
