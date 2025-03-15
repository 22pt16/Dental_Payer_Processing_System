from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

    
class PayerGroup(db.Model):
    __tablename__ = 'payer_groups'
    group_id = db.Column(db.String(50), primary_key=True)  # Alphanumeric ID (e.g., "DD" for Delta Dental)
    group_name = db.Column(db.String(255), nullable=False, unique=True)  # Name of the group (e.g., "Delta Dental")


class Payer(db.Model):
    __tablename__ = 'payers'
    payer_id = db.Column(db.String(50), primary_key=True)  # Alphanumeric ID (e.g., "AARP1")
    payer_name = db.Column(db.String(255), nullable=False)  # Name of the payer (e.g., "Delta Dental of Arizona")
    pretty_name = db.Column(db.String(255))  # Standardized display name
    group_id = db.Column(db.String(50), db.ForeignKey('payer_groups.group_id'), nullable=False)  # Foreign key to PayerGroup


class PayerDetail(db.Model):
    __tablename__ = 'payer_details'
    detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique identifier (serial)
    payer_id = db.Column(db.String(50), db.ForeignKey('payers.payer_id'), nullable=False)  # Foreign key to Payers
    payer_name = db.Column(db.String(255), nullable=False)  # Payer name from raw data
    state = db.Column(db.String(2))  # State abbreviation (e.g., "AZ")
    source = db.Column(db.String(255))  # Source of the data (e.g., "Vyne", "Availity")