import { BaseCRUDAPIReadOnly } from "~/lib/api/base/base-clients";
import { IngredientFood } from "~/lib/api/types/recipe";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";

const prefix = "/api";
const exploreGroupSlug = (groupSlug: string | number) => `${prefix}/explore/groups/${groupSlug}`

const routes = {
    foodsGroupSlug: (groupSlug: string | number) => `${exploreGroupSlug(groupSlug)}/foods`,
    foodsGroupSlugFoodId: (groupSlug: string | number, foodId: string | number) => `${exploreGroupSlug(groupSlug)}/foods/${foodId}`,
};

export class PublicFoodsApi extends BaseCRUDAPIReadOnly<IngredientFood> {
    baseRoute = routes.foodsGroupSlug(this.groupSlug);
    itemRoute = (itemId: string | number) => routes.foodsGroupSlugFoodId(this.groupSlug, itemId);

    constructor(requests: ApiRequestInstance, private readonly groupSlug: string) {
        super(requests);
    }
}
