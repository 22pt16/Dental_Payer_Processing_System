import os
import sys
import pandas as pd
from dotenv import load_dotenv
from flask import Flask

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import db, PayerGroup, Payer, PayerDetail
from backend.app import app

load_dotenv()

with app.app_context():
    # Load Excel data
    df = pd.read_excel(os.path.join('GoLassie DB', 'Payers.xlsx'), sheet_name=None)

    # Process and insert data into the database
    for sheet_name, sheet_data in df.items():
        for _, row in sheet_data.iterrows():
            # Insert PayerGroup if it doesn't exist
            group = PayerGroup.query.filter_by(group_id=row['Group ID']).first()
            if not group:
                group = PayerGroup(group_id=row['Group ID'], group_name=row['Group Name'])
                db.session.add(group)
                db.session.commit()

            # Insert Payer
            payer = Payer(
                payer_id=row['Payer ID'],
                payer_name=row['Payer Name'],
                pretty_name=row.get('Pretty Name', row['Payer Name']),  # Use Payer Name if Pretty Name is missing
                group_id=row['Group ID']
            )
            db.session.add(payer)

            # Insert PayerDetail
            payer_detail = PayerDetail(
                payer_id=row['Payer ID'],
                payer_name=row['Payer Name'],
                state=row['State'],
                source=sheet_name  # Use the sheet name as the source
            )
            db.session.add(payer_detail)
    db.session.commit()