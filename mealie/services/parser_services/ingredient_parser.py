from abc import ABC, abstractmethod
from fractions import Fraction

from mealie.core.root_logger import get_logger
from mealie.schema.recipe import RecipeIngredient
from mealie.schema.recipe.recipe_ingredient import CreateIngredientFood, CreateIngredientUnit

from .crfpp.processor import CRFIngredient, convert_list_to_crf_model

logger = get_logger(__name__)


class ABCIngredientParser(ABC):
    """
    Abstract class for ingredient parsers.
    """

    @abstractmethod
    def parse(self, ingredients: list[str]) -> list[RecipeIngredient]:
        ...


class CRFPPIngredientParser(ABCIngredientParser):
    """
    Class for CRFPP ingredient parsers.
    """

    def __init__(self) -> None:
        pass

    def _crf_to_ingredient(self, crf_model: CRFIngredient) -> RecipeIngredient:
        ingredient = None

        try:
            ingredient = RecipeIngredient(
                title="",
                note=crf_model.comment,
                unit=CreateIngredientUnit(name=crf_model.unit),
                food=CreateIngredientFood(name=crf_model.name),
                disable_amount=False,
                quantity=float(sum(Fraction(s) for s in crf_model.qty.split())),
            )
        except Exception as e:
            # TODO: Capture some sort of state for the user to see that an exception occured
            logger.exception(e)
            ingredient = RecipeIngredient(
                title="",
                note=crf_model.input,
            )

        return ingredient

    def parse(self, ingredients: list[str]) -> list[RecipeIngredient]:
        crf_models = convert_list_to_crf_model(ingredients)
        return [self._crf_to_ingredient(crf_model) for crf_model in crf_models]
