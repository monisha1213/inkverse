from models import db
from datetime import datetime

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('bookmarks', lazy=True))
    story = db.relationship('Story', backref=db.backref('bookmarks', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'story_id', name='unique_user_story_bookmark'),
    )

    def __repr__(self):
        return f'<Bookmark user={self.user_id} story={self.story_id}>'