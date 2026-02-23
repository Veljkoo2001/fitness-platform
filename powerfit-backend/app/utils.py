import re
from datetime import datetime, timedelta
import jwt
from flask import current_app

def calculate_bmi(weight_kg, height_cm):
    """Izračunava BMI"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 1)

def get_bmi_category(bmi):
    """Vraca kategoriju BMI"""
    if bmi < 18.5:
        return 'Pothranjenost'
    elif bmi < 25:
        return 'Normalna tezina'
    elif bmi < 30: 
        return 'Prekomerna tezina'
    else:
        return 'Gojaznost'
    

def validate_email(email):
    """Validacija email formata"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def generate_token(user_id):
    """Generise JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

    return token

def verify_token(token):
    """Verifikuje JWT token"""
    try:
        payload = jwt.decode(
            token, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithms=['HS256']
        )
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
def get_personalized_message(questionnaire):
    """Generise personalizovanu poruku na osnovu upitnika"""
    bmi = questionnaire.bmi
    goals = questionnaire.goals

    messages = []

    #  BMI message
    if bmi < 18.5:
        messages.append("Vaš BMI je ispod preporučenog. Fokusiraćemo se na zdrav način povećanja telesne mase.")
    elif bmi < 25:
        messages.append("Vaš BMI je u idealnom opsegu. Radimo na održavanju i definisanju.")
    elif bmi < 30:
        messages.append("Vaš BMI je nešto viši. Preporučićemo vam kombinaciju treninga i ishrane za mršavljenje.")
    else:
        messages.append("Vaš BMI zahteva posebnu pažnju. Dobićete detaljan plan za postepeno mršavljenje.")

    # Poruka na osnovu ciljeva
    if 'lose_weight' in goals and 'gain_muscle' in goals:
        messages.append("Cilj vam je rekompozicija tela - istovremeno mršavljenje i dobijanje mišića. Ovo je izazovno ali moguće uz pravi pristup.")
    elif 'lose_weight' in goals:
        messages.append("Fokusiraćemo se na kalorijski deficit i kardio treninge za mršavljenje.")
    elif 'gain_muscle' in goals:
        messages.append("Dobićete plan za hipertrofiju sa fokusom na progresivno opterećenje.")
    
    return " ".join(messages)