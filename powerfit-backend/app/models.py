from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
from flask import current_app

db = SQLAlchemy()

class User(db.Model):
    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_bash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum('user','admin','trainer'), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #Relationships
    questionnaires = db.relationship('Questionnaire', backref='user', lazy=True)
    memberships = db.relationship('UserMembership', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_bash = bcrypt.hashpw(password.encode('utf-8'), salt)

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_bash)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name' : self.last_name,
            'email' : self.email,
            'phone' : self.phone,
            'role' : self.role,
            'created_at' : self.created_at.isoformat() if self.created_at else None
        }

class Questionnaire(db.Model):
    __tablename__ = 'questionnaires'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)  # u cm
    weight = db.Column(db.Float, nullable=False)  # u kg
    experience = db.Column(db.Enum('beginner', 'intermediate', 'advanced'), nullable=False)
    activity_level = db.Column(db.Enum('sedentary', 'moderate', 'active'), nullable=False)
    goals = db.Column(db.JSON, nullable=False)  # Čuva niz ciljeva
    notes = db.Column(db.Text)
    bmi = db.Column(db.Float)
    status = db.Column(db.Enum('pending', 'processed', 'contacted'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_bmi(self):
        height_m = self.height / 100
        return round(self.weight / (height_m * height_m), 1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'bmi': self.bmi,
            'experience': self.experience,
            'activity_level': self.activity_level,
            'goals': self.goals,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Membership(db.Model):
    __tablename__ = 'memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum('student', 'standard', 'premium', 'family'), nullable=False)
    sessions_12 = db.Column(db.Float)
    sessions_16 = db.Column(db.Float)
    sessions_31 = db.Column(db.Float)
    personal_trainer_price = db.Column(db.Float)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'sessions_12': self.sessions_12,
            'sessions_16': self.sessions_16,
            'sessions_31': self.sessions_31,
            'personal_trainer_price': self.personal_trainer_price,
            'description': self.description
        }

class UserMembership(db.Model):
    __tablename__ = 'user_memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    membership_id = db.Column(db.Integer, db.ForeignKey('memberships.id'), nullable=False)
    sessions_type = db.Column(db.Enum('12', '16', '31'), nullable=False)
    sessions_remaining = db.Column(db.Integer, nullable=False)
    price_paid = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    membership = db.relationship('Membership')

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_membership_id = db.Column(db.Integer, db.ForeignKey('user_memberships.id'))
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.Enum('card', 'cash', 'bank_transfer'), nullable=False)
    stripe_payment_id = db.Column(db.String(255))
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('unread', 'read', 'replied'), default='unread')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)