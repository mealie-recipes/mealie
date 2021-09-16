from sqlalchemy.orm import Session

from mealie.db.models.group import GroupMealPlan
from mealie.db.models.group.cookbook import CookBook
from mealie.db.models.group.webhooks import GroupWebhooksModel
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.group.webhook import ReadWebhook
from mealie.schema.meal_plan.new_meal import ReadPlanEntry

from ._new_access_model import NewAccessModel
from .meal_access_model import MealDataAccessModel

pk_id = "id"
pk_slug = "slug"
pk_token = "token"


def get_meal_dal(session: Session):
    return MealDataAccessModel(session, pk_id, GroupMealPlan, ReadPlanEntry)


def get_cookbook_dal(session: Session):
    return NewAccessModel(session, pk_id, CookBook, ReadCookBook)


def get_webhook_dal(session: Session):
    return NewAccessModel(session, pk_id, GroupWebhooksModel, ReadWebhook)
