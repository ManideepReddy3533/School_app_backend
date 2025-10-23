# # app/api/student/routes.py
from flask import Blueprint, request, jsonify, current_app, url_for
from app.models.models import Student, ClassFee, FeeInstallment, Payment, db
from datetime import date, timedelta
from werkzeug.security import generate_password_hash
import secrets

student_bp = Blueprint('student_bp', __name__)

# # @student_bp.route('/register', methods=['POST'])
# # def register_student():
# #     data = request.get_json()
# #     # required: name, email, class_name
# #     if Student.query.filter_by(email=data['email']).first():
# #         return jsonify(msg="Student already registered"), 400

# #     # look up class fee
# #     cf = ClassFee.query.filter_by(class_name=data['class_assigned']).first()
# #     if not cf:
# #         return jsonify(msg="Class fee not configured"), 400

# #     # create student (inactive until first term paid)
# #     student = Student(
        
# #     db.session.add(student)
# #     db.session.flush()  # so student.id exists
# @student_bp.route('/register', methods=['POST'])
# def register_student():
#     data = request.get_json()
#     if not data:
#         return jsonify(msg="No input provided"), 400

#     # -------------------------------
#     # Required fields check
#     # -------------------------------
#     name = data.get('name')
#     email = data.get('email')
#     class_assigned = data.get('class_assigned')

#     if not all([name, email, class_assigned]):
#         return jsonify(msg="name, email, and class_assigned are required"), 400

#     # -------------------------------
#     # Duplicate email check
#     # -------------------------------
#     if Student.query.filter_by(email=email).first():
#         return jsonify(msg="Student with this email already exists"), 409

#     # -------------------------------
#     # Look up class fee
#     # -------------------------------
#     cf = ClassFee.query.filter_by(class_name=class_assigned).first()
#     if not cf:
#         return jsonify(msg=f"Class fee not configured for {class_assigned}"), 400

#     # -------------------------------
#     # Create student (portal_access=False until first payment)
#     # -------------------------------
#     student = Student(
#         name=name,
#         email=email,
#         class_assigned=class_assigned,
#         parent_name=data.get('parent_name'),
#         mobile=data.get('mobile'),
#         address=data.get('address'),
#         portal_access=False,
#         password_hash=generate_password_hash("temporary123")
#     )

#     db.session.add(student)
#     db.session.flush()  # student.id available for installments

#     # -------------------------------
#     # Create fee installments based on class fee term split
#     # -------------------------------
#     term_split = cf.term_split  # e.g., {"t1":40, "t2":30, "t3":30}
#     total_fee = cf.total_fee

#     for term, pct in term_split.items():
#         amount = int(total_fee * pct / 100)
#         installment = FeeInstallment(
#             student_id=student.id,
#             term_number=int(term[1]),  # convert "t1" -> 1
#             amount=amount,
#             status='pending'
#         )
#         db.session.add(installment)

#     db.session.commit()
#     return jsonify(
#     msg=f"Student {student.name} registered successfully",
#     fee_details={
#         "total_fee": cf.total_fee,
#         "term_split": cf.term_split
#     }
# ), 201

  

#     # compute installments
#     total = int(cf.total_fee)
#     t1_pct = int(cf.term_split.get('t1', 40))
#     t2_pct = int(cf.term_split.get('t2', 30))
#     t3_pct = int(cf.term_split.get('t3', 30))
#     a1 = round(total * t1_pct / 100)
#     a2 = round(total * t2_pct / 100)
#     a3 = total - (a1 + a2)

#     # due dates: now (t1), +120 days (t2), +240 days (t3)  (example)
#     today = date.today()
#     inst1 = FeeInstallment(student_id=student.id, term_number=1, amount=a1, due_date=today + timedelta(days=0))
#     inst2 = FeeInstallment(student_id=student.id, term_number=2, amount=a2, due_date=today + timedelta(days=120))
#     inst3 = FeeInstallment(student_id=student.id, term_number=3, amount=a3, due_date=today + timedelta(days=240))
#     db.session.add_all([inst1,inst2,inst3])
#     db.session.flush()

#     # create payment record for term1
#     payment = Payment(student_id=student.id, installment_id=inst1.id, amount=a1, method='UPI', status='pending')
#     db.session.add(payment)
#     db.session.commit()

#     # produce a payment_url or payment_token for frontend (placeholder)
#     # In production, call gateway API to create a payment session and return URL
#     payment_url = url_for('payment.initiate_payment', _external=True, payment_id=payment.id)
#     return jsonify(msg="Registration created, pay first term", payment_id=payment.id, payment_url=payment_url), 201
# @student_bp.route('/info/<int:student_id>', methods=['GET'])
# def get_student_info(student_id):
#     student = Student.query.get(student_id)
#     if not student:
#         return jsonify(msg="Student not found"), 404

#     installments = FeeInstallment.query.filter_by(student_id=student.id).all()
#     payments = Payment.query.filter_by(student_id=student.id).all()

#     inst_list = [{
#         "term_number": inst.term_number,
#         "amount": inst.amount,
#         "due_date": inst.due_date.isoformat() if inst.due_date else None,
#         "status": inst.status
#     } for inst in installments]

#     pay_list = [{
#         "amount": pay.amount,
#         "method": pay.method,
#         "status": pay.status,
#         "paid_at": pay.paid_at.isoformat() if pay.paid_at else None
#     } for pay in payments]

#     return jsonify(
#         student={
#             "id": student.id,
#             "name": student.name,
#             "email": student.email,
#             "class_name": student.class_name,
#             "active": student.active
#         },
#         installments=inst_list,
#         payments=pay_list
#     ), 200
    
@student_bp.route('/register', methods=['POST'])
def register_student():
    data = request.get_json()
    # check duplicate email
    if Student.query.filter_by(email=data['email']).first():
        return jsonify(msg="Student with this email already exists"), 400

    # look up class fee
    cf = ClassFee.query.filter_by(class_name=data['class_assigned']).first()
    if not cf:
        return jsonify(msg="Class fee not configured"), 400

    # create student
    student = Student(
        name=data['name'],
        email=data['email'],
       # # or hashed later
        class_assigned=data['class_assigned'],
        parent_name=data.get('parent_name'),
        mobile=data.get('mobile'),
        address=data.get('address'),
        portal_access=False,
        password_hash=generate_password_hash("1234578")

    )
    db.session.add(student)
    db.session.flush()  # student.id available

    # compute installments
    total = int(cf.total_fee)
    t1_pct = int(cf.term_split.get('t1', 40))
    t2_pct = int(cf.term_split.get('t2', 30))
    t3_pct = int(cf.term_split.get('t3', 30))
    a1 = round(total * t1_pct / 100)
    a2 = round(total * t2_pct / 100)
    a3 = total - (a1 + a2)

    today = date.today()
    inst1 = FeeInstallment(student_id=student.id, term_number=1, amount=a1, due_date=today)
    inst2 = FeeInstallment(student_id=student.id, term_number=2, amount=a2, due_date=today + timedelta(days=120))
    inst3 = FeeInstallment(student_id=student.id, term_number=3, amount=a3, due_date=today + timedelta(days=240))
    db.session.add_all([inst1, inst2, inst3])
    db.session.flush()

    # create payment record for term1
    payment = Payment(student_id=student.id, installment_id=inst1.id, amount=a1, method='UPI', status='pending')
    db.session.add(payment)
    db.session.commit()

    # generate payment URL (placeholder)
    payment_url = url_for('payment.initiate_payment', _external=True, payment_id=payment.id)

    # final combined response
    return jsonify(
        msg=f"Student {student.name} registered successfully",
        fee_details={
            "total_fee": cf.total_fee,
            "term_split": cf.term_split
        },
        payment={
            "payment_id": payment.id,
            "amount": a1,
            "status": payment.status,
            "payment_url": payment_url
        }
    ), 201
