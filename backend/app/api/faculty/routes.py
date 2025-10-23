# app/api/faculty/routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity
from werkzeug.security import check_password_hash
from app.models.models import Faculty, db
from app.utils.decorators import role_required

faculty_bp = Blueprint('faculty_bp', __name__)

# ----------------------------
# Faculty Login
# ----------------------------
@faculty_bp.route('/login', methods=['POST'])
def login_faculty():
    data = request.get_json()
    faculty = Faculty.query.filter_by(email=data['email']).first()
    
    if not faculty or not check_password_hash(faculty.password_hash, data['password']):
        return jsonify(msg='Invalid credentials'), 401

    access_token = create_access_token(
        identity=str(faculty.id),
        additional_claims={'role': 'faculty'}
    )
    return jsonify(access_token=access_token), 200


# ----------------------------
# Faculty Update Allowed Fields Only
# ----------------------------
@faculty_bp.route('/update-profile', methods=['PATCH'])
@role_required(['faculty'])
def update_faculty_data():
    faculty_id = get_jwt_identity()
    data = request.get_json()

    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify(msg="Faculty not found"), 404

    # Only allow updates for limited columns
    allowed_fields = ["subjects", "classes", "leisure_periods", "extra_activities"]
    updated_fields = {}

    for field in allowed_fields:
        if field in data:
            setattr(faculty, field, data[field])
            updated_fields[field] = data[field]

    if not updated_fields:
        return jsonify(msg="No valid fields to update"), 400

    db.session.commit()
    return jsonify(msg="Faculty data updated successfully", updated=updated_fields), 200


# ----------------------------
# Update attendance / marks (pending admin approval)
# ----------------------------
@faculty_bp.route('/update-class/<int:class_id>', methods=['POST'])
@role_required(['faculty'])
def update_class(class_id):
    faculty_id = get_jwt_identity()
    data = request.get_json()
    faculty = Faculty.query.get(faculty_id)
    
    if not faculty:
        return jsonify(msg="Faculty not found"), 404

    pending_updates = {
        'class_id': class_id,
        'marks': data.get('marks', {}),
        'attendance': data.get('attendance', {}),
        'approved': False
    }

    if not hasattr(faculty, 'pending_updates') or faculty.pending_updates is None:
        faculty.pending_updates = []

    faculty.pending_updates.append(pending_updates)
    db.session.commit()
    return jsonify(msg='Updates stored, pending admin approval', update=pending_updates), 200
