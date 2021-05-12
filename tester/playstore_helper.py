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

cat_to_slug = {
    'Art & Design': 'art-and-design',
    'Auto & Vehicles': 'auto-and-vehicles',
    'Beauty': 'beauty',
    'Books & Reference': 'books-and-reference',
    'Business': 'business',
    'Comics': 'comics',
    'Communication': 'communication',
    'Dating': 'dating',
    'Education': 'education',
    'Entertainment': 'entertainment',
    'Events': 'events',
    'Finance': 'finance',
    'Food & Drink': 'food-and-drink',
    'Health & Fitness': 'health-and-fitness',
    'House & Home': 'house-and-home',
    'Libraries & Demo': 'libraries-and-demo',
    'Lifestyle': 'lifestyle',
    'Maps & Navigation': 'maps-and-navigation',
    'Medical': 'medical',
    'Music & Audio': 'music-and-audio',
    'News & Magazines': 'news-and-magazines',
    'Parenting': 'parenting',
    'Personalization': 'personalization',
    'Photography': 'photography',
    'Productivity': 'productivity',
    'Shopping': 'shopping',
    'Social': 'social',
    'Sports': 'sports',
    'Tools': 'tools',
    'Travel & Local': 'travel-and-local',
    'Video Players & Editors': 'video-players',
    'Wear OS': 'android-wear',
    'Weather': 'weather',
    'Games': 'games',
    'Unknown': 'unknown',
}


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

def get_cat_slug(tags):
    try:
        return cat_to_slug[get_category_from_tags(tags)]
    except:
        return 'unknown'
