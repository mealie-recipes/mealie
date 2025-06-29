import { BaseCRUDAPIReadOnly } from "~/lib/api/base/base-clients";
import { RecipeCookBook } from "~/lib/api/types/cookbook";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";

const prefix = "/api";
const exploreGroupSlug = (groupSlug: string | number) => `${prefix}/explore/groups/${groupSlug}`

const routes = {
    cookbooksGroupSlug: (groupSlug: string | number) => `${exploreGroupSlug(groupSlug)}/cookbooks`,
    cookbooksGroupSlugCookbookId: (groupSlug: string | number, cookbookId: string | number) => `${exploreGroupSlug(groupSlug)}/cookbooks/${cookbookId}`,
};

export class PublicCookbooksApi extends BaseCRUDAPIReadOnly<RecipeCookBook> {
    constructor(requests: ApiRequestInstance, groupSlug: string) {
        super(
            requests,
            routes.cookbooksGroupSlug(groupSlug),
            (itemId: string | number) => routes.cookbooksGroupSlugCookbookId(groupSlug, itemId)
        );
    }
}
