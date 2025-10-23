# # app/__init__.py
# from flask import Flask
# from .models.models import db

# def create_app(config_object='config.Config'):
#     app = Flask(__name__)
#     app.config.from_object(config_object)

#     # Initialize SQLAlchemy
#     db.init_app(app)

#     with app.app_context():
#         db.create_all()  # Creates all tables if not exists

#     return app

# app/__init__.py
from flask import Flask
# from .models.models import db
# from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import JWTManager
# from flask_migrate import Migrate

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_object='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize DB & JWT, Migrate
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Import and register Blueprints
    # from .api.admin.routes import admin_bp
    # from .api.faculty.routes import faculty_bp
    
    # from .api.students.routes import students_bp
    # # from .api.travel.routes import travel_bp
    # # from .api.security.routes import security_bp

    # app.register_blueprint(admin_bp, url_prefix='/admin')
    # app.register_blueprint(faculty_bp, url_prefix='/faculty')
    # app.register_blueprint(students_bp, url_prefix='/student')
    # # app.register_blueprint(travel_bp, url_prefix='/travel')

    # # app.register_blueprint(security_bp, url_prefix='/security')
    from .api.admin.routes import admin_bp
    from .api.faculty.routes import faculty_bp
    from .api.students.routes import student_bp
    from .api.payments.routes import payment_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(faculty_bp, url_prefix='/faculty')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(payment_bp, url_prefix='/payments')

    with app.app_context():
        db.create_all()  # Creates tables if not exist

    return app

