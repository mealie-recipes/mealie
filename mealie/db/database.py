from db.db_mealplan import _Meals
from db.db_recipes import _Recipes
from db.db_settings import _Settings
from db.db_themes import _Themes

"""
Common Actions:
    - [ ] Create
    - [ ] Read
    - [ ] Update
    - [ ] Delete
    - [ ] Unpack Document Mongo Mostly.
    - [ ] Query by Primary Key

Recipe Actions
    - [ ] Query by Category
    - [ ] Query by dateAdded

Progress:
    - [x] Recipes
    - [ ] MealPlans
    - [ ] Site Settings
    - [ ] Themes

"""


class Database:
    def __init__(self) -> None:
        self.recipes = _Recipes()
        self.meals = _Meals()
        self.settings = _Settings()
        self.themes = _Themes()


db = Database()
