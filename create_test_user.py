from app import app, db
from models.user import User

with app.app_context():
    u = User(username="testwriter", email="test@example.com")
    u.set_password("password123")
    db.session.add(u)
    db.session.commit()
    print(User.query.all())