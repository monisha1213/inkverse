import os
import uuid
from flask import Flask, render_template, request, session, redirect, url_for
from functools import wraps
from werkzeug.utils import secure_filename
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
app.config['SECRET_KEY'] = 'dev-secret-key-change-this-later'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)


@app.context_processor
def inject_user():
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    else:
        current_user = None
    return dict(current_user=current_user)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    stories = Story.query.filter_by(status='published').order_by(Story.created_at.desc()).all()
    return render_template('home.html', stories=stories)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return render_template('register.html', error='Username or email already taken.')

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return render_template('login.html', error='Invalid username or password.')

        session['user_id'] = user.id
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    stories = Story.query.filter_by(author_id=session['user_id']).all()
    return render_template('dashboard.html', stories=stories)


@app.route('/stories/new', methods=['GET', 'POST'])
@login_required
def create_story():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        genre = request.form.get('genre')
        status = request.form.get('status')

        if not title:
            return render_template('create_story.html', error='Title is required.')

        cover_filename = None
        file = request.files.get('cover_image')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            cover_filename = unique_filename

        new_story = Story(
            title=title,
            description=description,
            genre=genre,
            status=status,
            cover_image=cover_filename,
            author_id=session['user_id']
        )
        db.session.add(new_story)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('create_story.html')


@app.route('/stories/<int:story_id>')
def view_story(story_id):
    story = Story.query.get_or_404(story_id)
    return render_template('view_story.html', story=story)


@app.route('/stories/<int:story_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_story(story_id):
    story = Story.query.get_or_404(story_id)

    if story.author_id != session['user_id']:
        return "You are not allowed to edit this story.", 403

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        genre = request.form.get('genre')
        status = request.form.get('status')

        if not title:
            return render_template('edit_story.html', story=story, error='Title is required.')

        file = request.files.get('cover_image')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            story.cover_image = unique_filename

        story.title = title
        story.description = description
        story.genre = genre
        story.status = status

        db.session.commit()

        return redirect(url_for('view_story', story_id=story.id))

    return render_template('edit_story.html', story=story)


@app.route('/stories/<int:story_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_story(story_id):
    story = Story.query.get_or_404(story_id)

    if story.author_id != session['user_id']:
        return "You are not allowed to delete this story.", 403

    if request.method == 'POST':
        db.session.delete(story)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('delete_story.html', story=story)


@app.route('/stories/<int:story_id>/chapters/new', methods=['GET', 'POST'])
@login_required
def create_chapter(story_id):
    story = Story.query.get_or_404(story_id)

    if story.author_id != session['user_id']:
        return "You are not allowed to add chapters to this story.", 403

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            return render_template('create_chapter.html', story=story, error='Title and content are required.')

        existing_chapters = Chapter.query.filter_by(story_id=story.id).count()
        next_number = existing_chapters + 1

        new_chapter = Chapter(
            story_id=story.id,
            chapter_number=next_number,
            title=title,
            content=content
        )
        db.session.add(new_chapter)
        db.session.commit()

        return redirect(url_for('view_story', story_id=story.id))

    return render_template('create_chapter.html', story=story)


@app.route('/stories/<int:story_id>/chapters/<int:chapter_number>')
def read_chapter(story_id, chapter_number):
    story = Story.query.get_or_404(story_id)
    chapter = Chapter.query.filter_by(story_id=story_id, chapter_number=chapter_number).first_or_404()

    all_chapters = story.chapters
    current_index = all_chapters.index(chapter)
    prev_chapter = all_chapters[current_index - 1] if current_index > 0 else None
    next_chapter = all_chapters[current_index + 1] if current_index < len(all_chapters) - 1 else None

    return render_template(
        'read_chapter.html',
        story=story,
        chapter=chapter,
        prev_chapter=prev_chapter,
        next_chapter=next_chapter
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)