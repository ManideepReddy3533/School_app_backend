# app/api/payment/routes.py
from flask import Blueprint, request, jsonify
from app.models.models import Payment, FeeInstallment, Student, db
from datetime import datetime

# payment_bp = Blueprint('payment_bp', __name__)
# from flask import Blueprint, request, jsonify
# from app.models.models import Payment, db
# from datetime import datetime

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/initiate/<int:payment_id>', methods=['GET'])
def initiate_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify(msg="Payment not found"), 404

    # placeholder for real payment gateway URL
    payment_url = f"https://sandbox.paymentgateway.com/pay/{payment_id}"
    return jsonify(
        msg="Payment initiation created",
        payment_id=payment.id,
        payment_url=payment_url
    ), 200

@payment_bp.route('/callback', methods=['POST'])
def payment_callback():
    payload = request.get_json()
    # Gateways differ. Validate signature, parse payload.
    payment_ref = payload.get('payment_reference')  # gateway id
    our_id = payload.get('client_payment_id')  # we sent payment.id to gateway
    status = payload.get('status')  # "PAID" or "FAILED"
    amount = payload.get('amount')

    payment = Payment.query.get(our_id)
    if not payment:
        return jsonify(msg="Payment not found"), 404

    # Idempotency: if already paid, ignore
    if payment.status == 'paid':
        return jsonify(msg="Already processed"), 200

    if status.lower() == 'paid':
        payment.status = 'paid'
        payment.gateway_reference = payment_ref
        payment.paid_at = datetime.utcnow()

        # mark installment paid
        inst = FeeInstallment.query.get(payment.installment_id)
        if inst:
            inst.status = 'paid'
            inst.payment_id = payment.id

        # activate student (grant portal access) on first-term payment
        student = Student.query.get(payment.student_id)
        if student and inst and inst.term_number == 1:
            student.active = True
            # generate credentials (random password)
            pwd = secrets.token_urlsafe(8)
            # you should hash password before storing
            student.password_hash = generate_password_hash(pwd)
            # send email with credentials (see send_email helper)
            send_credential_email(student.email, student.name, pwd)

        db.session.commit()
        return jsonify(msg="Payment processed"), 200

    else:
        payment.status = 'failed'
        db.session.commit()
        return jsonify(msg="Payment failed"), 200
