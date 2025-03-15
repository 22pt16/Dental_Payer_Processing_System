# backend/app.py
from flask import Flask, jsonify

import os
from dotenv import load_dotenv
import sys
# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.models import db, PayerGroup, Payer, PayerDetail
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Add this
db.init_app(app)

@app.route('/')
def home():
    return "Welcome to the Dental Payer System!"

if __name__ == '__main__':
    app.run(debug=True)