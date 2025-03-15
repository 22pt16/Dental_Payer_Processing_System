import os
import sys
import pandas as pd
from dotenv import load_dotenv
from flask import Flask

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import db, PayerDetail, Payer, PayerGroup
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
    """Normalize column names based on mapping"""
    if df.columns.duplicated().any():
        print(f"Warning: Found duplicate columns: {df.columns[df.columns.duplicated()]}")
        df = df.loc[:, ~df.columns.duplicated()]
    
    df.columns = [COLUMN_MAPPING.get(col.strip() if isinstance(col, str) else col, col) for col in df.columns]
    
    required_columns = ['payer_name', 'payer_id']
    for col in required_columns:
        if col not in df.columns:
            print(f"Warning: Required column '{col}' not found. Creating empty column.")
            df[col] = ''
    
    df = df.fillna({'payer_name': '', 'payer_id': '', 'state': '', 'source': ''})
    return df

def handle_merged_cells(df):
    """Handle merged cells and ensure consistent row data"""
    df = df.ffill()
    return df

def safe_extract(row, column, default=''):
    """Safely extract a value from a row, handling Series objects"""
    try:
        value = row[column]
        if isinstance(value, pd.Series):
            return value.iloc[0] if not value.empty and not pd.isna(value.iloc[0]) else default
        else:
            return value if not pd.isna(value) else default
    except (KeyError, IndexError):
        return default

def main():
    """Main function to orchestrate the data loading process"""
    with app.app_context():
        try:
            print("Loading Excel file...")
            excel_file = os.path.join('GoLassie DB', 'Payers.xlsx')
            rows_processed = 0
            
            for sheet_name in pd.ExcelFile(excel_file).sheet_names:
                if sheet_name in IGNORE_SHEETS:
                    print(f"Skipping sheet: {sheet_name}")
                    continue
                
                print(f"Loading sheet: {sheet_name}")
                sheet_data = pd.read_excel(
                    excel_file, 
                    sheet_name=sheet_name,
                    header=0,
                    na_values=['NA', ''],
                    keep_default_na=True
                )
                
                sheet_data.dropna(how='all', inplace=True)
                sheet_data.dropna(axis=1, how='all', inplace=True)
                
                sheet_data = normalize_columns(sheet_data)
                print(f"Columns after normalization for {sheet_name}: {list(sheet_data.columns)}")
                
                sheet_data = handle_merged_cells(sheet_data)
                
                for index, row in sheet_data.iterrows():
                    rows_processed += 1
                    
                    if rows_processed % 100 == 0:
                        print(f"Processed {rows_processed} rows total. Currently on sheet: {sheet_name}")
                    
                    try:
                        payer_name = str(safe_extract(row, 'payer_name'))
                        payer_id = str(safe_extract(row, 'payer_id'))
                        state = str(safe_extract(row, 'state')) if 'state' in row else None
                        source = sheet_name
                        
                        if not payer_name.strip():
                            print(f"Skipping row {index + 1} in {sheet_name} due to empty payer_name")
                            continue
                        
                        # Use placeholder for empty payer_id
                        if not payer_id.strip():
                            payer_id = f"ID{index}_{sheet_name}"
                        
                        # Check if payer_id already exists in payers
                        existing_payer = db.session.query(Payer).filter_by(payer_id=payer_id).first()
                        if not existing_payer:
                            payer = Payer(
                                payer_id=payer_id,
                                payer_name=payer_name,
                                pretty_name=payer_name,
                                group_id="UNKNOWN"
                            )
                            db.session.add(payer)
                        
                        payer_detail = PayerDetail(
                            payer_id=payer_id,
                            payer_name=payer_name,
                            state=state,
                            source=source
                        )
                        db.session.add(payer_detail)
                        
                        if rows_processed % 100 == 0:
                            try:
                                db.session.commit()
                                print(f"Committed {rows_processed} rows")
                            except Exception as e:
                                print(f"Error committing at {rows_processed}: {e}")
                                db.session.rollback()
                                continue
                    
                    except Exception as e:
                        print(f"Error processing row {index + 1} in {sheet_name}: {e}")
                        continue
            
            # Final commit
            try:
                db.session.commit()
                print(f"Total rows processed: {rows_processed}")
            except Exception as e:
                print(f"Error in final commit: {e}")
                db.session.rollback()
            
            print("Data loading complete!")
            
        except Exception as e:
            print(f"Error in data loading process: {e}")
            db.session.rollback()
            print("Changes rolled back due to error.")

if __name__ == "__main__":
    main()