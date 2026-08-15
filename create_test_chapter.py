from app import app, db
from models.user import User
from models.story import Story
from models.chapter import Chapter

with app.app_context():
    # Find the story we already created
    story = Story.query.filter_by(title="The Last Ember").first()

    # Create two chapters linked to that story
    chapter1 = Chapter(
        story_id=story.id,
        chapter_number=1,
        title="The Spark",
        content="In the beginning, there was only a single flame..."
    )

    chapter2 = Chapter(
        story_id=story.id,
        chapter_number=2,
        title="The Fading Light",
        content="As days passed, the flame grew weaker..."
    )

    db.session.add(chapter1)
    db.session.add(chapter2)
    db.session.commit()

    # Confirm it worked - print all chapters for this story, in order
    print(f"Chapters for '{story.title}':")
    for ch in story.chapters:
        print(f"  {ch.chapter_number}. {ch.title}")