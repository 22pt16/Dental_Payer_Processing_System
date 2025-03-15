# scripts/load_data.py
import os
import sys
import pandas as pd
from dotenv import load_dotenv
from flask import Flask

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import db, PayerDetail
from backend.app import app

load_dotenv()

COLUMN_MAPPING = {
    'Payer ID': 'payer_id',
    'ID': 'payer_id',
    'Payer_ID': 'payer_id',
    'Payer Name': 'payer_name',
    'Name': 'payer_name',
    'Payer_Name': 'payer_name',
    'State': 'state',
    'ST': 'state',
    'Source': 'source',
    'Payer Identification Information': 'payer_name',
    'Payer': 'payer_name',
    'Payer Short Name': 'payer_name',
}

IGNORE_SHEETS = ['Legend', 'Legend (1)', 'OpenDental']

def normalize_columns(df):
    df.columns = [COLUMN_MAPPING.get(col.strip(), col.strip().lower()) for col in df.columns]
    df = df.fillna({'payer_name': '', 'payer_id': '', 'state': '', 'source': ''})
    return df

with app.app_context():
    print("Loading Excel file...")
    df = pd.read_excel(os.path.join('GoLassie DB', 'Payers.xlsx'), sheet_name=None)

    for sheet_name, sheet_data in df.items():
        if sheet_name in IGNORE_SHEETS:
            print(f"Skipping sheet: {sheet_name}")
            continue

        print(f"Processing sheet: {sheet_name}")
        sheet_data = normalize_columns(sheet_data)

        for index, row in sheet_data.iterrows():
            if index % 100 == 0:
                print(f"Processing row {index + 1} in sheet: {sheet_name}")

            payer_name = str(row.get('payer_name', ''))
            payer_id = str(row.get('payer_id', ''))
            state = str(row.get('state', ''))
            source = sheet_name

            if not payer_name:
                print(f"Skipping row {index + 1} due to missing payer_name")
                continue

            try:
                payer_detail = PayerDetail(
                    payer_id=payer_id if payer_id else f"ID{index}",
                    payer_name=payer_name,
                    state=state if state else None,
                    source=source
                )
                db.session.add(payer_detail)
            except Exception as e:
                print(f"Error inserting row {index + 1}: {e}")
                continue

    print("Committing changes...")
    db.session.commit()
    print("Raw data loaded successfully into payer_details!")