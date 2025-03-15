from flask import Flask, jsonify
from backend.models import db, PayerGroup, Payer, PayerDetail  # Fixed typo here
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
db.init_app(app)

@app.route('/')
def home():
    return "Welcome to the Dental Payer System!"

if __name__ == '__main__':
    app.run(debug=True)