# backend/routes.py
from flask import jsonify, request
from fuzzywuzzy import fuzz
from models import db, PayerDetail, Payer

def get_similarity_score(name1, name2):
    return fuzz.ratio(name1.lower(), name2.lower())

def init_routes(app):
    @app.route('/')
    def home():
        return "Welcome to the Dental Payer System!"

    @app.route('/api/unmapped', methods=['GET'])
    def get_unmapped():
        details = db.session.query(PayerDetail).all()
        payer_groups = {}
        unmapped = []
        
        for detail in details:
            matched = False
            for key in payer_groups:
                canonical_id, canonical_name = key
                name_score = get_similarity_score(detail.payer_name, canonical_name)
                if name_score > 70 and name_score <= 85:
                    unmapped.append({
                        "detail_id": detail.detail_id,
                        "payer_name": detail.payer_name,
                        "payer_id": detail.payer_id,
                        "source": detail.source,
                        "state": detail.state
                    })
                    matched = True
                    break
            if not matched and detail.payer_id not in [k[0] for k in payer_groups]:
                payer_groups[(detail.payer_id, detail.payer_name)] = [detail]
        
        return jsonify(unmapped)

    @app.route('/api/map_payer', methods=['POST'])
    def map_payer():
        data = request.json
        detail = PayerDetail.query.get(data['detail_id'])
        detail.payer_id = data['payer_id']
        db.session.commit()
        return {"status": "success"}

    @app.route('/api/update_pretty_name', methods=['POST'])
    def update_pretty_name():
        data = request.json
        payer = Payer.query.get(data['payer_id'])
        payer.pretty_name = data['pretty_name']
        db.session.commit()
        return {"status": "success"}

    @app.route('/api/payers', methods=['GET'])
    def get_payers():
        payers = db.session.query(Payer).all()
        return jsonify([{
            "payer_id": p.payer_id,
            "payer_name": p.payer_name,
            "pretty_name": p.pretty_name
        } for p in payers])