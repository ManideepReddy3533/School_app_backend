# app/models/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#from sqlalchemy.dialects.postgresql import JSON
 # adjust import if needed
from sqlalchemy.dialects.mysql import JSON
from app import db



# -------------------------------
# Admin Model
# -------------------------------
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------------------
# Faculty Model
# -------------------------------
class Faculty(db.Model):
    __tablename__ = 'faculties'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Faculty-editable fields with safe defaults
    subjects = db.Column(JSON, default=dict)
    classes = db.Column(JSON, default=dict)
    leisure_periods = db.Column(JSON, default=dict)
    extra_activities = db.Column(JSON, default=dict)
    attendance = db.Column(JSON, default=dict)
    
    salary_status = db.Column(db.String(20), default='Pending')
    approved_by_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------------------
# Student Model
# -------------------------------
# from datetime import datetime, date
  # adjust import if needed



# ---------------------------------------
# CLASS FEE STRUCTURE
# ---------------------------------------
class ClassFee(db.Model):
    __tablename__ = "class_fees"
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "Nursery", "1st"
    total_fee = db.Column(db.Integer, nullable=False)  # Total annual fee
    term_split = db.Column(JSON, nullable=False, default=lambda: {"t1": 40, "t2": 30, "t3": 30})
    # JSON to represent term-wise fee % split


# ---------------------------------------
# STUDENTS TABLE
# ---------------------------------------
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)  # set after payment
    class_assigned = db.Column(db.VARCHAR(50), nullable=False)  # match with ClassFee.class_name
    parent_name = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    address = db.Column(db.Text)

    fee_status = db.Column(db.String(20), default='pending')  # pending/partial/paid
    attendance = db.Column(JSON)
    marks = db.Column(JSON)
    activities = db.Column(JSON)

    portal_access = db.Column(db.Boolean, default=False)  # becomes True after first term payment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to installments and payments
    installments = db.relationship('FeeInstallment', backref='student', lazy=True)
    payments = db.relationship('Payment', backref='student', lazy=True)


# ---------------------------------------
# FEE INSTALLMENTS (TERM-WISE)
# ---------------------------------------
class FeeInstallment(db.Model):
    __tablename__ = "fee_installments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    term_number = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    amount = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, paid, waived

    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)


# ---------------------------------------
# PAYMENTS (via UPI, CARD, NEFT, RTGS, etc.)
# ---------------------------------------
class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    installment_id = db.Column(db.Integer, db.ForeignKey('fee_installments.id'), nullable=True)

    amount = db.Column(db.Integer, nullable=False)
    method = db.Column(db.String(50), nullable=False)  # UPI, CARD, NEFT, RTGS, etc.
    status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    gateway_reference = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)

# -------------------------------
# Travel Model
# -------------------------------
class Travel(db.Model):
    __tablename__ = 'travels'
    bus_no = db.Column(db.String(20), primary_key=True)
    route = db.Column(db.String(100))
    route_fee = db.Column(db.Numeric)
    students = db.Column(JSON)
    faculty = db.Column(JSON)
    fee_status = db.Column(JSON)
    boarding_days = db.Column(JSON)

# -------------------------------
# Security Model
# -------------------------------
class Security(db.Model):
    __tablename__ = 'security_staffs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.Text)
    shift = db.Column(db.String(20))
    working_hours = db.Column(db.Integer)
    salary_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
