from app import app, db
from models.user import User
from models.story import Story

with app.app_context():
    print("All users:")
    for u in User.query.all():
        print(f"  id={u.id}, username={u.username}, email={u.email}")

    print("All stories:")
    for s in Story.query.all():
        print(f"  id={s.id}, title={s.title}, author_id={s.author_id}")