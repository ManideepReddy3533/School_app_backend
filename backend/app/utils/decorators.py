# app/utils/decorators.py
from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask import jsonify

def role_required(allowed_roles):
    """
    Decorator to restrict access to specific roles
    Usage: @role_required(['admin'])
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') not in allowed_roles:
                return jsonify(msg='Access forbidden: insufficient role'), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
