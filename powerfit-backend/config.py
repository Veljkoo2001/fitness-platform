import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #Basic configuration 
    SECRET_KEY= os.environ.get('SECRET_KEY')

    #Database 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    #Email Setiings (for sent confirmations)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    #Stripe(for paid)
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')