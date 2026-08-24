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
    constructor(requests: ApiRequestInstance, groupSlug: string) {
        super(
            requests,
            routes.categoriesGroupSlug(groupSlug),
            (itemId: string | number) => routes.categoriesGroupSlugCategoryId(groupSlug, itemId)
        );
    }
}

export class PublicTagsApi extends BaseCRUDAPIReadOnly<RecipeTag> {
    constructor(requests: ApiRequestInstance, groupSlug: string) {
        super(
            requests,
            routes.tagsGroupSlug(groupSlug),
            (itemId: string | number) => routes.tagsGroupSlugTagId(groupSlug, itemId)
        );
    }
}

export class PublicToolsApi extends BaseCRUDAPIReadOnly<RecipeTool> {
    constructor(requests: ApiRequestInstance, groupSlug: string) {
        super(
            requests,
            routes.toolsGroupSlug(groupSlug),
            (itemId: string | number) => routes.toolsGroupSlugToolId(groupSlug, itemId)
        );
    }
}
