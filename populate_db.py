from app import create_app
from app.extensions import db
from app.database.models.levels import Level, Category, Option
from app.database.models.lessons import Lesson  

app = create_app()

with app.app_context():
    # Clean slate
    db.drop_all()
    db.create_all()
    print("Database tables recreated.")

    # ======================
    # 1. Levels
    # ======================
    levels = [
        Level(id=1, name="American English Level 1"),
        Level(id=2, name="American English Level 2"),
        Level(id=3, name="American English Level 3")
    ]
    db.session.add_all(levels)

    # ======================
    # 2. Categories
    # ======================
    categories = [
        # Level 1 Categories
        Category(id=1, title="Alphabet", level_id=1),
        Category(id=2, title="Numbers", level_id=1),
        Category(id=3, title="Colors", level_id=1),      
        Category(id=4, title="Verbs", level_id=1),
        Category(id=5, title="Food", level_id=1),
        Category(id=6, title="Vegetables", level_id=1),
        Category(id=7, title="Fruits", level_id=1),
        Category(id=8, title="Drinks and Candies", level_id=1),
        
        # Level 2 Categories
        Category(id=9, title="Wild Animals", level_id=2),
        Category(id=10, title="Numbers", level_id=2),
        Category(id=11, title="Weather", level_id=2),
        Category(id=12, title="Dogs", level_id=2),
        Category(id=13, title="Balls", level_id=2),
        Category(id=14, title="Insects", level_id=2),
        Category(id=15, title="Christmas", level_id=2),
        Category(id=16, title="Dolphin", level_id=2),
        
        # Level 3 Categories
        Category(id=17, title="Clothes", level_id=3),
        Category(id=18, title="Transport", level_id=3),
        Category(id=19, title="Family", level_id=3),
        Category(id=20, title="Shapes", level_id=3),
        Category(id=21, title="Shower", level_id=3),
        Category(id=22, title="Nature", level_id=3),
        Category(id=23, title="School", level_id=3),
        Category(id=24, title="Chair", level_id=3)
    ]
    db.session.add_all(categories)

    # ======================
    # 3. Options
    # ======================
    options = []
    # Each category gets 5 options in this order:
    option_types = ["Vocabulary", "Listening", "Reading", "Memory", "Writing"]
    
    for category in categories:
        for i, option_name in enumerate(option_types, start=1):
            option_id = (category.id - 1) * 5 + i
            options.append(
                Option(id=option_id, name=option_name, category_id=category.id)
            )
    
    db.session.add_all(options)

    # ======================
    # 4. Lessons
    # ======================
    lessons = [
        # Level 1 - Colors - Vocabulary (Option ID = (3-1)*5 + 1 = 11)
        Lesson(
            level_id=1,
            category_id=3,
            option_id=11,
            lesson_number=3,
            title="Colors Vocabulary 3",
            content="Learn color words: red, blue, green, orange, yellow, black, brown, purple, sky blue, pink",
        ),
        
        # Level 1 - Colors - Listening (Option ID = (3-1)*5 + 2 = 12)
        Lesson(
            level_id=1,
            category_id=3,
            option_id=12,
            lesson_number=3,
            title="Colors Listening 3",
            content="Identify colors by sound: Brown, Orange",
        ),
        
        Lesson(
            level_id=1,
            category_id=3,
            option_id=12,
            lesson_number=5,
            title="Colors Listening 5",
            content="Identify colors by sound: Brown, Orange",
        ),

        Lesson(
            level_id=1,
            category_id=3,
            option_id=12,
            lesson_number=9,
            title="Colors Listening 9",
            content="Advanced color listening: 'orange', 'green', 'black', 'pink'",
        ),

        # Level 1 - Colors - Reading (Option ID = (3-1)*5 + 3 = 13)
        Lesson(
            level_id=1,
            category_id=3,
            option_id=13,
            lesson_number=3,
            title="Colors Reading 3",
            content="Read color name: Black, Brown",
        ),

        Lesson(
            level_id=1,
            category_id=3,
            option_id=13,
            lesson_number=7,
            title="Colors Reading 7",
            content="Read color name: Blue, Brown, Black, Pink",
        ),

        # Level 1 - Colors - Memory (Option ID = (3-1)*5 + 4 = 14)
        Lesson(
            level_id=1,
            category_id=3,
            option_id=14,
            lesson_number=2,
            title="Colors Memory 2",
            content="Match color shades to their names",
        ),
        
        # Level 1 - Colors - Writing (Option ID = (3-1)*5 + 5 = 15)
        Lesson(
            level_id=1,
            category_id=3,
            option_id=15,
            lesson_number=1,
            title="Colors Writing 1",
            content="Write the displayed color: Black",
        ),
        
    ]
    
    db.session.add_all(lessons)
    db.session.commit()
    print("Database populated successfully with fixed IDs!")