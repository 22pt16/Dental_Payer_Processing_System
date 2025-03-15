# scripts/init_unmapped.py
import os
import sys
import pandas as pd


# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import db, Payer
from backend.app import app

with app.app_context():
    unmapped = Payer(
        payer_id="UNMAPPED",
        payer_name="Unmapped Payer",
        pretty_name="Unmapped",
        group_id="UNKNOWN"
    )
    db.session.add(unmapped)
    db.session.commit()
    print("Added UNMAPPED payer to payers table.")