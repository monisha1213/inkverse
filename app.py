from flask import Flask
from models import db
from models.user import User
from models.story import Story
from models.chapter import Chapter
from models.comment import Comment
from models.like import Like
from models.bookmark import Bookmark
from models.follow import Follow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inkverse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def home():
    return "InkVerse is alive!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)