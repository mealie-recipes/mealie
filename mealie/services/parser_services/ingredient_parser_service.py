from mealie.schema.recipe import RecipeIngredient
from mealie.services._base_http_service.http_services import UserHttpService

from .ingredient_parser import ABCIngredientParser, RegisteredParser, get_parser


class IngredientParserService(UserHttpService):
    parser: ABCIngredientParser

    def __init__(self, parser: RegisteredParser = RegisteredParser.nlp, *args, **kwargs) -> None:
        self.set_parser(parser)
        super().__init__(*args, **kwargs)

    def set_parser(self, parser: RegisteredParser) -> None:
        self.parser = get_parser(parser)

    def populate_item(self) -> None:
        """Satisfy abstract method"""
        pass

    def parse_ingredient(self, ingredient: str) -> RecipeIngredient:
        parsed = self.parser.parse([ingredient])

        if parsed:
            return parsed[0]
        # TODO: Raise Exception

    def parse_ingredients(self, ingredients: list[str]) -> list[RecipeIngredient]:
        parsed = self.parser.parse(ingredients)

        if parsed:
            return parsed
        # TODO: Raise Exception
