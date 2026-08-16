import os
import uuid
from datetime import timedelta
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this-later')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

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
    search_query = request.args.get('q', '').strip()
    genre_filter = request.args.get('genre', '').strip()

    query = Story.query.filter_by(status='published')

    if search_query:
        query = query.filter(Story.title.ilike(f'%{search_query}%'))

    if genre_filter:
        query = query.filter_by(genre=genre_filter)

    stories = query.order_by(Story.created_at.desc()).all()

    genres = ['Fantasy', 'Romance', 'Mystery', 'Sci-Fi', 'Horror', 'Adventure', 'Other']

    return render_template(
        'home.html',
        stories=stories,
        genres=genres,
        search_query=search_query,
        genre_filter=genre_filter
    )


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
        remember_me = request.form.get('remember_me')

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return render_template('login.html', error='Invalid username or password.')

        session['user_id'] = user.id
        session.permanent = bool(remember_me)
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


@app.route('/bookmarks')
@login_required
def bookmarks():
    user_bookmarks = Bookmark.query.filter_by(user_id=session['user_id']).all()
    bookmarked_stories = [b.story for b in user_bookmarks]
    return render_template('bookmarks.html', stories=bookmarked_stories)


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

    user_has_liked = False
    user_has_bookmarked = False
    if 'user_id' in session:
        user_has_liked = Like.query.filter_by(user_id=session['user_id'], story_id=story.id).first() is not None
        user_has_bookmarked = Bookmark.query.filter_by(user_id=session['user_id'], story_id=story.id).first() is not None

    like_count = Like.query.filter_by(story_id=story.id).count()

    return render_template(
        'view_story.html',
        story=story,
        user_has_liked=user_has_liked,
        like_count=like_count,
        user_has_bookmarked=user_has_bookmarked
    )


@app.route('/stories/<int:story_id>/like', methods=['POST'])
@login_required
def toggle_like(story_id):
    story = Story.query.get_or_404(story_id)

    existing_like = Like.query.filter_by(user_id=session['user_id'], story_id=story.id).first()

    if existing_like:
        db.session.delete(existing_like)
    else:
        new_like = Like(user_id=session['user_id'], story_id=story.id)
        db.session.add(new_like)

    db.session.commit()

    return redirect(url_for('view_story', story_id=story.id))


@app.route('/stories/<int:story_id>/bookmark', methods=['POST'])
@login_required
def toggle_bookmark(story_id):
    story = Story.query.get_or_404(story_id)

    existing_bookmark = Bookmark.query.filter_by(user_id=session['user_id'], story_id=story.id).first()

    if existing_bookmark:
        db.session.delete(existing_bookmark)
    else:
        new_bookmark = Bookmark(user_id=session['user_id'], story_id=story.id)
        db.session.add(new_bookmark)

    db.session.commit()

    return redirect(url_for('view_story', story_id=story.id))


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

    comments = Comment.query.filter_by(chapter_id=chapter.id).order_by(Comment.created_at.desc()).all()

    return render_template(
        'read_chapter.html',
        story=story,
        chapter=chapter,
        prev_chapter=prev_chapter,
        next_chapter=next_chapter,
        comments=comments
    )


@app.route('/chapters/<int:chapter_id>/comments', methods=['POST'])
@login_required
def add_comment(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    content = request.form.get('content')

    if content and content.strip():
        new_comment = Comment(
            user_id=session['user_id'],
            chapter_id=chapter.id,
            content=content.strip()
        )
        db.session.add(new_comment)
        db.session.commit()

    return redirect(url_for('read_chapter', story_id=chapter.story_id, chapter_number=chapter.chapter_number))


@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    published_stories = Story.query.filter_by(author_id=user.id, status='published').order_by(Story.created_at.desc()).all()

    is_following = False
    if 'user_id' in session and session['user_id'] != user.id:
        is_following = Follow.query.filter_by(follower_id=session['user_id'], following_id=user.id).first() is not None

    return render_template(
        'profile.html',
        profile_user=user,
        stories=published_stories,
        is_following=is_following
    )


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()
        user.bio = bio
        db.session.commit()
        return redirect(url_for('profile', username=user.username))

    return render_template('edit_profile.html')


@app.route('/profile/<username>/follow', methods=['POST'])
@login_required
def toggle_follow(username):
    user_to_follow = User.query.filter_by(username=username).first_or_404()

    if user_to_follow.id == session['user_id']:
        return redirect(url_for('profile', username=username))

    existing_follow = Follow.query.filter_by(follower_id=session['user_id'], following_id=user_to_follow.id).first()

    if existing_follow:
        db.session.delete(existing_follow)
    else:
        new_follow = Follow(follower_id=session['user_id'], following_id=user_to_follow.id)
        db.session.add(new_follow)

    db.session.commit()

    return redirect(url_for('profile', username=username))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)