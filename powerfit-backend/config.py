import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #Basic configuration 
    SECRET_KEY= os.environ.get('SECRET_KEY')

    #Database 
    SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    #Email Setiings (for sent confirmations)