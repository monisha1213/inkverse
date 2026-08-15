from models import db
from datetime import datetime

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('likes', lazy=True))
    story = db.relationship('Story', backref=db.backref('likes', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'story_id', name='unique_user_story_like'),
    )

    def __repr__(self):
        return f'<Like user={self.user_id} story={self.story_id}>'