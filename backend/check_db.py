# from sqlalchemy import text
# from app import create_app, db

# app = create_app()
# app.app_context().push()  # activate app context

# # Test DB connection
# try:
#     db.session.execute(text("SELECT 1"))
#     print("Database connected successfully!")
# except Exception as e:
#     print("Database connection failed:", e)

# # List tables
# print(db.engine.table_names())


from sqlalchemy import text, inspect
from app import create_app, db
from app.models.models import Faculty

# Create app and push context
app = create_app()
app.app_context().push()

# Test DB connection
try:
    db.session.execute(text("SELECT 1"))
    print("Database connected successfully!")
except Exception as e:
    print("Database connection failed:", e)

# List all tables
inspector = inspect(db.engine)
tables = inspector.get_table_names()
print("Tables in database:", tables)




with app.app_context():
    f = Faculty.query.filter_by(name="John Doe").first()
    print(f.approved_by_admin)  # shoul
