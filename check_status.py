from app import app, db
from models.story import Story

with app.app_context():
    stories = Story.query.all()
    for s in stories:
        print(f"id={s.id}, title={s.title}, status={s.status}")