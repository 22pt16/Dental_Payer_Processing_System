import os
import sys
import pandas as pd
from dotenv import load_dotenv
from flask import Flask
from fuzzywuzzy import fuzz

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database models and Flask app
from backend.models import db, PayerDetail, Payer, PayerGroup  # Add PayerGroup here
from backend.app import app

# Load environment variables from .env file
load_dotenv()

# Define a mapping for column name normalization
COLUMN_MAPPING = {
    'Payer ID': 'payer_id',
    'ID': 'payer_id',
    'Payer_ID': 'payer_id',
    'Payer Name': 'payer_name',
    'Name': 'payer_name',
    'Payer_Name': 'payer_name',
    'Group ID': 'group_id',
    'Group_ID': 'group_id',
    'Group Name': 'group_name',
    'Group_Name': 'group_name',
    'State': 'state',
    'ST': 'state',
    'Pretty Name': 'pretty_name',
    'Source': 'source',
    'Payer Identification Information': 'payer_name',  # Map to payer_name
    'Payer': 'payer_name',  # Map to payer_name
    'Payer Short Name': 'payer_name',  # Map to payer_name
    'Transaction Type (ID)': 'transaction_type',  # Optional field
    'Enrollment Required': 'enrollment_required',  # Optional field
    'Service': 'service',  # Optional field
    'NPI': 'npi',  # Optional field
    '5010': 'x5010',  # Optional field
    'Additional Info': 'additional_info',  # Optional field
    'ERA/EFT Enrollment Level': 'era_enrollment_level',  # Optional field
    'ERA Enrollment Type': 'era_enrollment_type',  # Optional field
    'Requires EFT for ERA Enrollment': 'requires_eft',  # Optional field
    'ERA Payer Enrollment Form Required': 'era_form_required',  # Optional field
    'ERA Paper RA Shut Off': 'era_paper_shutoff',  # Optional field
    'ERA Un-Enrollment Process': 'era_unenrollment_process',  # Optional field
    'Late/Missing EFT and ERA Resolution': 'late_missing_resolution',  # Optional field
}

# Sheets to ignore
IGNORE_SHEETS = ['Legend', 'Legend (1)', 'OpenDental']

# Define a mapping for pretty names
PRETTY_NAMES = {
    "DELTA DENTAL OF ARIZONA": "Delta Dental of Arizona",
    "AARP Dental Insurance Plan": "AARP",
}

# Function to normalize column names
def normalize_columns(df):
    df.columns = [COLUMN_MAPPING.get(col.strip(), col.strip()) for col in df.columns]
    return df

# Function to find a matching payer using fuzzy matching
def find_matching_payer(payer_name, existing_payers):
    for payer in existing_payers:
        if fuzz.ratio(payer_name.lower(), payer.payer_name.lower()) > 80:  # Adjust threshold as needed
            return payer
    return None

# Use the Flask app context to interact with the database
with app.app_context():
    # Load Excel data
    print("Loading Excel file...")
    df = pd.read_excel(os.path.join('GoLassie DB', 'Payers.xlsx'), sheet_name=None)

    # Get all existing payers for deduplication
    existing_payers = db.session.query(Payer).all()

    # Process and insert data into the database
    for sheet_name, sheet_data in df.items():
        # Skip ignored sheets
        if sheet_name in IGNORE_SHEETS:
            print(f"Skipping sheet: {sheet_name}")
            continue

        print(f"Processing sheet: {sheet_name}")

        # Normalize column names
        sheet_data = normalize_columns(sheet_data)

        # Process each row in the sheet
        for index, row in sheet_data.iterrows():
            # Debugging: Print progress for every 100 rows
            if index % 100 == 0:
                print(f"Processing row {index + 1} in sheet: {sheet_name}")

            # Skip rows with missing payer_name or payer_id
            if pd.isna(row['payer_name']) or pd.isna(row['payer_id']):
                print(f"Skipping row {index + 1} due to missing payer_name or payer_id")
                continue

            # Get payer details
            payer_id = str(row['payer_id'])  # Convert payer_id to string
            payer_name = row['payer_name']

            # Check if the payer already exists (exact match)
            payer = db.session.query(Payer).filter(Payer.payer_id == payer_id).first()

            # If no exact match, check for fuzzy matches
            if not payer:
                payer = find_matching_payer(payer_name, existing_payers)

            # If no match, create a new payer
            if not payer:
                # Assign a group_id based on payer name
                if "Delta Dental" in payer_name:
                    group_id = "DD"  # Delta Dental group
                else:
                    group_id = "UNKNOWN"  # Default group

                # Check if the group_id exists in the payer_groups table
                group = db.session.query(PayerGroup).filter(PayerGroup.group_id == group_id).first()
                if not group:
                    # Create a new payer_group if it doesn't exist
                    group = PayerGroup(
                        group_id=group_id,
                        group_name=group_id  # Use group_id as the group_name for now
                    )
                    db.session.add(group)
                    db.session.commit()  # Commit the group first

                # Assign a pretty name
                pretty_name = PRETTY_NAMES.get(payer_name, payer_name)

                # Create a new payer
                payer = Payer(
                    payer_id=payer_id,
                    payer_name=payer_name,
                    pretty_name=pretty_name,
                    group_id=group_id
                )
                db.session.add(payer)
                db.session.commit()  # Commit the payer first
                existing_payers.append(payer)  # Add to existing payers list

            # Insert PayerDetail
            payer_detail = PayerDetail(
                payer_id=payer.payer_id,
                payer_name=payer_name,
                state=row.get('state', None),  # Handle missing state
                source=sheet_name  # Use the sheet name as the source
            )
            db.session.add(payer_detail)
    
    # Commit all changes to the database
    print("About to commit changes to the database...")
    db.session.commit()
    print("Changes committed successfully!")