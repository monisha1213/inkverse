from models import db
from datetime import datetime

class Chapter(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    story = db.relationship('Story', backref=db.backref('chapters', lazy=True, order_by='Chapter.chapter_number'))

    def __repr__(self):
        return f'<Chapter {self.chapter_number}: {self.title}>'