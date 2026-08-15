from app import app, db
from models.user import User
from models.story import Story

with app.app_context():
    # Find the user we created earlier
    user = User.query.filter_by(username="testwriter").first()

    # Create a new story linked to that user
    story = Story(
        title="The Last Ember",
        description="A fantasy story about the last flame in a dying world.",
        genre="Fantasy",
        status="draft",
        author_id=user.id
    )

    db.session.add(story)
    db.session.commit()

    print(story)
    print("Written by:", story.author.username)
    print("This author's stories:", user.stories)