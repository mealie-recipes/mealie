import { BaseCRUDAPIReadOnly } from "~/lib/api/base/base-clients";
import { RecipeCategory, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";

const prefix = "/api";
const exploreGroupSlug = (groupSlug: string | number) => `${prefix}/explore/groups/${groupSlug}`

const routes = {
    categoriesGroupSlug: (groupSlug: string | number) => `${exploreGroupSlug(groupSlug)}/organizers/categories`,
    categoriesGroupSlugCategoryId: (groupSlug: string | number, categoryId: string | number) => `${exploreGroupSlug(groupSlug)}/organizers/categories/${categoryId}`,
    tagsGroupSlug: (groupSlug: string | number) => `${exploreGroupSlug(groupSlug)}/organizers/tags`,
    tagsGroupSlugTagId: (groupSlug: string | number, tagId: string | number) => `${exploreGroupSlug(groupSlug)}/organizers/tags/${tagId}`,
    toolsGroupSlug: (groupSlug: string | number) => `${exploreGroupSlug(groupSlug)}/organizers/tools`,
    toolsGroupSlugToolId: (groupSlug: string | number, toolId: string | number) => `${exploreGroupSlug(groupSlug)}/organizers/tools`,
};

export class PublicCategoriesApi extends BaseCRUDAPIReadOnly<RecipeCategory> {
    baseRoute = routes.categoriesGroupSlug(this.groupSlug);
    itemRoute = (itemId: string | number) => routes.categoriesGroupSlugCategoryId(this.groupSlug, itemId);

    constructor(requests: ApiRequestInstance, private readonly groupSlug: string) {
        super(requests);
    }
}

export class PublicTagsApi extends BaseCRUDAPIReadOnly<RecipeTag> {
    baseRoute = routes.tagsGroupSlug(this.groupSlug);
    itemRoute = (itemId: string | number) => routes.tagsGroupSlugTagId(this.groupSlug, itemId);

    constructor(requests: ApiRequestInstance, private readonly groupSlug: string) {
        super(requests);
    }
}

export class PublicToolsApi extends BaseCRUDAPIReadOnly<RecipeTool> {
    baseRoute = routes.toolsGroupSlug(this.groupSlug);
    itemRoute = (itemId: string | number) => routes.toolsGroupSlugToolId(this.groupSlug, itemId);

    constructor(requests: ApiRequestInstance, private readonly groupSlug: string) {
        super(requests);
    }
}
