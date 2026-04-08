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
    constructor(requests: ApiRequestInstance, groupSlug: string) {
        super(
            requests,
            routes.foodsGroupSlug(groupSlug),
            (itemId: string | number) => routes.foodsGroupSlugFoodId(groupSlug, itemId)
        );
    }
}
