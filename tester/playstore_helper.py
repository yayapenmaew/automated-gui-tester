import re

PLAYSTORE_CATEGORIES = [
    "Art & Design",
    "Auto & Vehicles",
    "Beauty",
    "Books & Reference",
    "Bussiness",
    "Comics",
    "Communication",
    "Dating",
    "Education",
    "Entertainment",
    "Events",
    "Finance",
    "Food & Drink",
    "Health & Fitness",
    "House & Home",
    "Libraries & Demo",
    "Lifestyle",
    "Maps & Navigation",
    "Medical",
    "Music & Audio",
    "News & Megazines",
    "Parenting",
    "Personalisation",
    "Photography",
    "Productivity",
    "Shopping",
    "Social",
    "Sports",
    "Tools",
    "Travel & Local",
    "Video Players & Editors",
    "Wear OS by Google",
    "Weather",
]

GAME_CATEGORIES = [
    "Action",
    "Adventure",
    "Arcade",
    "Board",
    "Card",
    "Casino",
    "Casual",
    "Educational",
    "Music",
    "Puzzle",
    "Racing",
    "Role Playing",
    "Simulation",
    "Sports",
    "Strategy",
    "Trivia",
    "Word",
]

GAME_ATTRIBUTES = [
    "Offline",
    "Single player",
    "Realistic"
]


def get_category_from_tags(tags):
    for tag in tags:
        for cat in PLAYSTORE_CATEGORIES:
            if cat.lower() in tag.lower():
                return cat

    '''If main cat not found, search for game cats.'''
    for tag in tags:
        for game_genre in GAME_CATEGORIES:
            if game_genre.lower() in tag.lower():
                return "Games"

    return "Unknown"


