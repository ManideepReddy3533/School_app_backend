# app/api/admin/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from app.models.models import Admin, Faculty,db,ClassFee,Student,FeeInstallment
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.decorators import role_required

admin_bp = Blueprint('admin_bp', __name__)

# ----------------------------
# Admin Register (one-time or super-admin)
# ----------------------------
@admin_bp.route('/register', methods=['POST'])
def register_admin():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    admin = Admin(username=data['username'], email=data['email'], password_hash=hashed_password)
    db.session.add(admin)
    db.session.commit()
    return jsonify(msg='Admin registered'), 201

# ----------------------------
# Admin Login
# ----------------------------
@admin_bp.route('/login', methods=['POST'])
def login_admin():
    data = request.get_json()
    admin = Admin.query.filter_by(username=data['username']).first()
    if not admin or not check_password_hash(admin.password_hash, data['password']):
        return jsonify(msg='Invalid credentials'), 401

    # access_token = create_access_token(identity=admin.id, additional_claims={'role': 'admin'})
    access_token = create_access_token(
    identity=str(admin.id),  # convert integer ID to string
    additional_claims={'role': 'admin'})

    return jsonify(access_token=access_token), 200

# ----------------------------
# Example protected route
# ----------------------------
@admin_bp.route('/all-faculties', methods=['GET'])
@role_required(['admin'])
def all_faculties():
    from app.models.models import Faculty
    faculties = Faculty.query.all()
    output = []
    for f in faculties:
        output.append({'id': f.id, 'name': f.name, 'approved': f.approved_by_admin})
    return jsonify(faculties=output)

@admin_bp.route('/register-faculty', methods=['POST'])
@role_required(['admin'])
def register_faculty():
    data = request.get_json()

    # Check if email already exists
    if Faculty.query.filter_by(email=data['email']).first():
        return jsonify(msg="Faculty already exists"), 400

    # Create faculty record
    faculty = Faculty(
        name=data['name'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        # subjects=data.get('subjects', {}),
        # classes=data.get('classes', {}),
        salary_status=data.get('salary_status', 'Pending'),
        approved_by_admin=False
    )
    db.session.add(faculty)
    db.session.commit()

    return jsonify(msg="Faculty registered successfully (pending approval)"), 201


# ----------------------------
# Approve Faculty
# ----------------------------
@admin_bp.route('/approve-faculty/<int:faculty_id>', methods=['PATCH'])
@role_required(['admin'])
def approve_faculty(faculty_id):
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify(msg="Faculty not found"), 404

    faculty.approved_by_admin = True
    db.session.commit()

    return jsonify(msg=f"Faculty {faculty.name} approved successfully"), 200


# ----------------------------
# View Pending Faculty Updates
# ----------------------------
@admin_bp.route('/pending-updates', methods=['GET'])
@role_required(['admin'])
def view_pending_updates():
    faculties = Faculty.query.all()
    pending = []

    for f in faculties:
        if getattr(f, "pending_updates", None):
            for upd in f.pending_updates:
                if not upd.get("approved", False):
                    pending.append({
                        "faculty_id": f.id,
                        "faculty_name": f.name,
                        "update": upd
                    })

    return jsonify(pending_updates=pending), 200


# ----------------------------
# Approve Faculty Update
# ----------------------------
@admin_bp.route('/approve-update/<int:faculty_id>', methods=['PATCH'])
@role_required(['admin'])
def approve_faculty_update(faculty_id):
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return jsonify(msg="Faculty not found"), 404

    if not faculty.pending_updates:
        return jsonify(msg="No pending updates found"), 404

    # Mark all as approved (or modify this as per your use-case)
    for upd in faculty.pending_updates:
        upd["approved"] = True

    db.session.commit()
    return jsonify(msg=f"All pending updates for {faculty.name} approved"), 200

#fee Payments Sructure Management


# admin/routes.py (add)
@admin_bp.route('/class-fee', methods=['POST'])
@role_required(['admin'])
def set_class_fee():
    data = request.get_json()
    # { "class_name": "1st", "total_fee": 33800, "term_split": {"t1":40,"t2":30,"t3":30} }
    cf = ClassFee.query.filter_by(class_name=data['class_name']).first()
    if cf:
        cf.total_fee = data['total_fee']
        cf.term_split = data.get('term_split', cf.term_split)
    else:
        cf = ClassFee(class_name=data['class_name'],
                      total_fee=data['total_fee'],
                      term_split=data.get('term_split', {"t1":40,"t2":30,"t3":30}))
        db.session.add(cf)
    db.session.commit()
    return jsonify(msg="Class fee saved"), 200

@admin_bp.route('/class-fee/<class_name>', methods=['GET'])
@role_required(['admin'])
def get_class_fee(class_name):
    cf = ClassFee.query.filter_by(class_name=class_name).first()
    if not cf: return jsonify(msg="Not found"), 404
    return jsonify(class_name=cf.class_name, total_fee=cf.total_fee, term_split=cf.term_split)

