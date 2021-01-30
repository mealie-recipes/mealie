from typing import List
from models.category_models import Category
from db.database import db

def get_all() -> List[Category]:
    categories = db.category.all()
    print(categories)
    [print(cat) for cat in categories]
    return [Category(name=cat) for cat in categories]
    return [Category(name="Hej"), Category(name="Fra"), Category(name="Serveren")];