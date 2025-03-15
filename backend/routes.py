# backend/routes.py
from flask import jsonify, request
from fuzzywuzzy import fuzz
from models import db, PayerDetail, Payer, PayerGroup
from sqlalchemy import or_, not_
import re

def get_similarity_score(name1, name2):
    return fuzz.ratio(name1.lower(), name2.lower())

def generate_pretty_name(payer_name):
    name = re.sub(r'\s*\([^)]*\)', '', payer_name)
    suffixes = ['Inc', 'Corporation', 'LLC', 'Administrators', 'Services', 'Plans']
    for suffix in suffixes:
        name = re.sub(rf'\s+{suffix}$', '', name, flags=re.IGNORECASE)
    words = name.split()
    return ''.join(word.capitalize() for word in words[:2]) if len(words) > 1 else name.capitalize()

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
        unmapped = []
        payer_names = {p.payer_id: p.payer_name for p in db.session.query(Payer).all()}
        
        for detail in details:
            matched = False
            for payer_id, canonical_name in payer_names.items():
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
            if not matched and detail.payer_id not in payer_names:
                unmapped.append({
                    "detail_id": detail.detail_id,
                    "payer_name": detail.payer_name,
                    "payer_id": detail.payer_id,
                    "source": detail.source,
                    "state": detail.state
                })

        total_unmapped = db.session.query(PayerDetail).filter(
            or_(
                PayerDetail.payer_id.in_(
                    db.session.query(PayerDetail.payer_id).filter(
                        PayerDetail.payer_name.in_([
                            d.payer_name for d in details if any(
                                70 < get_similarity_score(d.payer_name, pn) <= 85
                                for pn in payer_names.values()
                            )
                        ])
                    )
                ),
                not_(PayerDetail.payer_id.in_(payer_names.keys()))
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
                "pretty_name": p.pretty_name if p.pretty_name else generate_pretty_name(p.payer_name),
                "group_id": p.group_id
            } for p in payers],
            "total": total,
            "page": page,
            "per_page": per_page
        })

    @app.route('/api/groups', methods=['GET'])
    def get_groups():
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 1000))
        offset = (page - 1) * per_page
        
        groups = db.session.query(PayerGroup).offset(offset).limit(per_page).all()
        total = db.session.query(PayerGroup).count()
        
        def infer_hierarchy(group, all_groups, processed=None):
            if processed is None:
                processed = set()
            if group.group_id in processed:
                return None  # Avoid infinite recursion
            processed.add(group.group_id)
            
            children = []
            for other in all_groups:
                if other.group_id != group.group_id:
                    similarity = fuzz.ratio(group.group_name.lower(), other.group_name.lower())
                    if similarity > 80 and other.group_name.startswith(group.group_name):
                        child = infer_hierarchy(other, all_groups, processed)
                        if child:
                            children.append(child)
            return {
                "group_id": group.group_id,
                "group_name": group.group_name,
                "children": children
            }
        
        # Find top-level groups (not children of others)
        top_level = []
        for g in groups:
            is_child = False
            for other in groups:
                if g.group_id != other.group_id and fuzz.ratio(g.group_name.lower(), other.group_name.lower()) > 80 and g.group_name.startswith(other.group_name):
                    is_child = True
                    break
            if not is_child:
                top_level.append(infer_hierarchy(g, groups))
        
        return jsonify({
            "groups": top_level,
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