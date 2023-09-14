import { BaseCRUDAPIReadOnly } from "~/lib/api/base/base-clients";
import { RecipeCookBook } from "~/lib/api/types/cookbook";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";

const prefix = "/api";

const routes = {
    cookbooksGroupSlug: (groupSlug: string | number) => `${prefix}/explore/cookbooks/${groupSlug}`,
    cookbooksGroupSlugCookbookId: (groupSlug: string | number, cookbookId: string | number) => `${prefix}/explore/cookbooks/${groupSlug}/${cookbookId}`,
};

export class PublicCookbooksApi extends BaseCRUDAPIReadOnly<RecipeCookBook> {
    baseRoute = routes.cookbooksGroupSlug(this.groupSlug);
    itemRoute = (itemId: string | number) => routes.cookbooksGroupSlugCookbookId(this.groupSlug, itemId);

    constructor(requests: ApiRequestInstance, private readonly groupSlug: string) {
        super(requests);
    }
}
