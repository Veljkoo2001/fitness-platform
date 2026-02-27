from flask import Blueprint, request, jsonify
from flask_cors import CORS
from app.models import db, Questionnaire, User, Membership
from app.utils import get_bmi_category ,calculate_bmi, get_personalized_message, generate_token, verify_token
from datetime import datetime

import re

api = Blueprint('api', __name__)
CORS(api) #Dozvoljava zahteve sa frontenda

# ==================== JAVNE RUTE ====================

@api.route('/health', methods=['GET'])
def health_check():
    """Proverava da li API radi"""
    return jsonify({
        'status': 'ok',
        'message': 'PowerFit Gym API je aktivan',
        'timestamp': datetime.utcnow().isoformat()
    })
@api.route('/questionnaire', methods=['POST'])
def submit_questionnaire():
    """Prima podatke iz fitness upitnika"""
    try:
        data = request.json

        # Validacija obaveznih polja
        required_fields = ['firstName', 'lastName', 'age', 'height',
                           'weight', 'experience', 'activityLevel', 'goals']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Nedostaje polje: {field}'
                }), 400
            
        # Izracunaj BMI
        bmi = calculate_bmi(float(data['weight']), float(data['height']))

        # Proveri da li je korisnik ulogovan (ako ima token u headeru)
        user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            user_id = verify_token(token)

        # Kreiraj novi upitnik
        questionnaire = Questionnaire(
            user_id=user_id,
            first_name=data['firstName'],
            last_name=data['lastName'],
            age=int(data['age']),
            height=float(data['height']),
            weight=float(data['weight']),
            experience=data['experience'],
            activity_level=data['activityLevel'],
            goals=data['goals'],
            notes=data.get('notes', ''),
            bmi=bmi
        )

        db.session.add(questionnaire)
        db.session.commit()

        # Generisi personalizovanu poruku 

        personal_message = get_personalized_message(
            bmi=questionnaire.bmi,
            goals=questionnaire.goals
        )

        return jsonify({
            'success': True,
            'message': 'Upitnik uspešno poslat',
            'data': {
                'id': questionnaire.id,
                'bmi': bmi,
                'bmi_category': get_bmi_category(bmi),
                'personal_message': personal_message
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Došlo je do greške: {str(e)}'
        }), 500
    
@api.route('/memberships', methods=['GET'])
def get_memberships():
    """Vraca sve dostupne clanarine"""
    memberships = Membership.query.filter_by(is_active=True).all()
    return jsonify({
        'success': True,
        'data': [m.to_dict() for m in memberships]
    })

@api.route('/contact', methods=['POST'])
def contact_message():
    """Prima kontakt poruke"""
    try:
        data = request.json

        # TODO: Sačuvaj u bazu i pošalji email
        # Za sada samo vraćamo uspeh

        return jsonify({
            'success': True,
            'message': 'Poruka je uspešno poslata'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500         

# ==================== KORISNIČKE RUTE ====================
@api.route('/auth/register', methods=['POST'])
def register():
    """Registracija novog korisnika"""
    try:
        data = request.json

        # Validacija
        required_fields = ['firstName', 'lastName', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Nedostaje polje: {field}'
                }), 400

        # Provera email formata
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, data['email']):
            return jsonify({
                'success': False,
                'message': 'Email nije ispravnog formata'
            }), 400

        # Provera da li korisnik vec postoji
        exciting = User.query.filter_by(email=data['email']).first()
        if exciting:
            return jsonify({
                'success': False,
                'message': 'Korisnik sa ovim emailom već postoji'
            }), 400
        
        # Provera lozinke (min 6 karaktera)
        if len(data['password']) < 6:
            return jsonify({
                'success': False,
                'message': 'Lozinka mora imati najmanje 6 karaktera'
            }), 400

        # Kreiranje novog korisnika
        user = User(
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            phone=data.get('phone', '')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Generisi token 
        token = generate_token(user.id)

        return jsonify({
            'success': True,
            'message': 'Uspešna registracija',
            'data': {
                'user': user.to_dict(),
                'token': token
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Došlo je do greške: {str(e)}'
        }), 500

@api.route('/auth/login', methods=['POST'])
def login():
    """Prijava korisnika"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email i lozinka su obavezni'
            }), 400

        # Pronadji korisnika
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Pogrešan email ili lozinka'
            }) , 401
        
        if not user.is_active: 
            return jsonify({
                'success': False,
                'message': 'Nalog je deaktiviran'
            }), 401
        
        # Generisi token
        token = generate_token(user.id)

        return jsonify({
            'success': True,
            'message': 'Uspešna prijava',
            'data': {
                'user': user.to_dict(),
                'token': token
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Došlo je do greške: {str(e)}"
        }), 500
    
@api.route('/user/profile', methods=['GET'])
def get_profile():
    """Vraca profil korisnika (zahteva token)"""
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return jsonify({'success': False, 'message': 'Niste autorizovani'}), 401
    
    try:
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)

        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Nevažeći token'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Korisnik ne postoji'
            }),404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    
    except Exception as e: 
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    
# ==================== ADMIN RUTE ====================

@api.route('/admin/questionnaires', methods=['GET'])
def get_all_questionnaires():
    """Vraca sve upitnike (samo za admina)"""
    #TODO: Dodati proveru za admina
    questionnaires = Questionnaire.query.order_by(Questionnaire.created_at.desc()).all()
    return jsonify({
        'success': True,
        'data': [q.to_dict() for q in questionnaires]
    })

@api.route('/admin/questionnaires/<int:id>/status', methods=['PUT'])
def update_questionnaire_status(id):
    """Azurira status upitnika"""
    try:
        data = request.json
        questionnaire = Questionnaire.query.get_or_404(id)

        questionnaire.status = data['status']
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Status ažuriran',
            'data': questionnaire.to_dict()
        }),200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    
# ==================== POMOĆNE FUNKCIJE ====================
def get_bmi_category(bmi):
    """Vraca kategoriju BMI"""
    if bmi < 18.5:
        return 'Pothranjenost'
    elif 18.5 <= bmi < 25:
        return 'Normalna težina'
    elif 25 <= bmi < 30:
        return 'Prekomerna težina'
    else:
        return 'Gojaznost'
    
def get_personalized_message(bmi, goals):
    """Generiše personalizovanu poruku na osnovu upitnika"""
    messages = []
    
    if bmi < 18.5:
        messages.append("Vaš BMI ukazuje na pothranjenost. Fokusiraćemo se na zdrav način povećanja telesne mase.")
    elif 18.5 <= bmi < 25:
        messages.append("Vaš BMI je u normalnom rasponu. Naš program će vam pomoći da održite dobru formu i zdravlje.")
    elif 25 <= bmi < 30:
        messages.append("Vaš BMI ukazuje na prekomernu težinu. Naš program će vam pomoći da smršate i poboljšate kondiciju.")
    else:
        messages.append("Vaš BMI ukazuje na gojaznost. Dobićete detaljan plan za postepeno mršavljenje.")

    if 'lose_weight' in goals and 'gain_muscle' in goals:
        messages.append("Vaši ciljevi su gubitak težine i dobijanje mišićne mase. Naš program će kombinovati kardio i trening snage.")
    elif 'lose_weight' in goals:
        messages.append("Vaš cilj je gubitak težine. Fokusiraćemo se na kardio trening i zdravu ishranu.")
    elif 'gain_muscle' in goals:
        messages.append("Vaš cilj je dobijanje mišićne mase. Naš program će se fokusirati na trening snage i adekvatan unos proteina.")

    return " ".join(messages)