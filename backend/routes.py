# backend/routes.py
from flask import jsonify, request
from fuzzywuzzy import fuzz
from models import db, PayerDetail, Payer, PayerGroup
from sqlalchemy import or_, not_
import re


def get_similarity_score(name1, name2):
    return fuzz.ratio(name1.lower(), name2.lower())

def generate_pretty_name(payer_name):
    """Generate a clean pretty name from payer_name."""
    # Remove parentheses and contents
    name = re.sub(r'\s*\([^)]*\)', '', payer_name)
    # Remove common suffixes
    suffixes = ['Inc', 'Corporation', 'LLC', 'Administrators', 'Services', 'Plans']
    for suffix in suffixes:
        name = re.sub(rf'\s+{suffix}$', '', name, flags=re.IGNORECASE)
    # Take first significant words (up to 2)
    words = name.split()
    return ' '.join(words[:2]) if len(words) > 1 else name


def init_routes(app):
    @app.route('/')
    def home():
        return "Welcome to the Dental Payer System!"

    @app.route('/api/unmapped', methods=['GET'])
    def get_unmapped():
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 100))
        offset = (page - 1) * per_page
        
        details = db.session.query(PayerDetail).offset(offset).limit(per_page).all()
        payer_groups = {}
        unmapped = []
        
        all_payers = db.session.query(Payer).all()
        payer_ids = [p.payer_id for p in all_payers]
        payer_names = {p.payer_id: p.payer_name for p in all_payers}
        for payer in all_payers:
            payer_groups[(payer.payer_id, payer.payer_name)] = []

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

        total_unmapped = db.session.query(PayerDetail).filter(
            or_(
                PayerDetail.payer_id.in_(
                    db.session.query(PayerDetail.payer_id).filter(
                        PayerDetail.payer_name.in_([
                            detail.payer_name for detail in details
                            if any(70 < get_similarity_score(detail.payer_name, payer_names.get(p_id, '')) <= 85
                                   for p_id in payer_ids)
                        ])
                    )
                ),
                not_(PayerDetail.payer_id.in_(payer_ids))
            )
        ).count()

        return jsonify({
            "unmapped": unmapped,
            "total": total_unmapped,
            "page": page,
            "per_page": per_page
        })

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
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        
        payers = db.session.query(Payer).offset(offset).limit(per_page).all()
        total = db.session.query(Payer).count()
        
        return jsonify({
            "payers": [{
                "payer_id": p.payer_id,
                "payer_name": p.payer_name,
                "pretty_name": generate_pretty_name(p.payer_name),
                "group_id": p.group_id
            } for p in payers],
            "total": total,
            "page": page,
            "per_page": per_page
        })

    @app.route('/api/groups', methods=['GET'])
    def get_groups():
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        
        groups = db.session.query(PayerGroup).offset(offset).limit(per_page).all()
        total = db.session.query(PayerGroup).count()
        
        return jsonify({
            "groups": [{
                "group_id": g.group_id,
                "group_name": g.group_name
            } for g in groups],
            "total": total,
            "page": page,
            "per_page": per_page
        })

    @app.route('/api/update_group', methods=['POST'])
    def update_group():
        data = request.json
        payer = Payer.query.get(data['payer_id'])
        group_id = data['group_id']
        
        group = PayerGroup.query.get(group_id)
        if not group:
            group = PayerGroup(group_id=group_id, group_name=group_id)
            db.session.add(group)
        
        payer.group_id = group_id
        db.session.commit()
        return {"status": "success"}