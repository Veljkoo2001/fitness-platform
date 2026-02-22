import re
from datetime import datetime, timedelta
import jwt
from flask import current_app

def calculate_bmi(weight_kg, height_cm):
    """Izračunava BMI"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 1)