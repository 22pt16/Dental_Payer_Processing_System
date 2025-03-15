# backend/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PayerGroup(db.Model):
    __tablename__ = 'payer_groups'
    group_id = db.Column(db.String(50), primary_key=True)  # Alphanumeric ID (e.g., "DD")
    group_name = db.Column(db.String(255), nullable=False, unique=True)  # Name of the group (e.g., "Delta Dental")

class Payer(db.Model):
    __tablename__ = 'payers'
    payer_id = db.Column(db.String(50), primary_key=True)  # Alphanumeric ID (e.g., "86027")
    payer_name = db.Column(db.String(255), nullable=False)  # Name of the payer (e.g., "Delta Dental of Arizona")
    pretty_name = db.Column(db.String(255), nullable=True)  # Standardized display name (e.g., "Delta Dental AZ")
    group_id = db.Column(db.String(50), db.ForeignKey('payer_groups.group_id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('payer_name', 'group_id', name='uq_payer_name_group'),)

class PayerDetail(db.Model):
    __tablename__ = 'payer_details'
    detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique identifier (serial)
    payer_id = db.Column(db.String(50), db.ForeignKey('payers.payer_id'), nullable=False, index=True)
    payer_name = db.Column(db.String(255), nullable=False)  # Payer name from raw data
    state = db.Column(db.String(2))  # State abbreviation (e.g., "AZ")
    source = db.Column(db.String(255))  # Source of the data (e.g., "Vyne", "Availity")