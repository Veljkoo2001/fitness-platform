from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from app.models import db

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicijalizacija ekstenzija
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app) # Dozvoli CORS za sve rute

    # Registracija blueprint-a
    from app.routes import api
    app.register_blueprint(api, url_prefix='/api')

    # Kreiraj tabele ako ne postoje
    with app.app_context():
        db.create_all()

        #Dodaj pocetne podatke za clanarine ako ih nema
        if Membership.query.count() == 0:
            seed_memberships()

    return app

def seed_memberships():
    """Dodaje pocetne pakete clanarina"""
    memberships = [
        Membership(
            name = 'Studentski',
            type = 'student',
             sessions_12=4500,
            sessions_16=5800,
            sessions_31=9900,
            personal_trainer_price=3500,
            description='Za studente sa važećim indeksom'
        ),
        Membership(
            name='Standardni',
            type='standard',
            sessions_12=5900,
            sessions_16=7200,
            sessions_31=12500,
            personal_trainer_price=3500,
            description='Standardni paket za sve članove'
        ),
        Membership(
            name='Premium',
            type='premium',
            sessions_12=7500,
            sessions_16=9800,
            sessions_31=15900,
            personal_trainer_price=2500,
            description='Premium paket sa svim uključenim uslugama'
        ),
        Membership(
            name='Porodični',
            type='family',
            sessions_12=9800,
            sessions_16=12500,
            sessions_31=22900,
            personal_trainer_price=3000,
            description='Porodični paket za 2 osobe'
        )
    ]

    for membership in memberships:
        db.session.add(membership)

    db.session.commit()