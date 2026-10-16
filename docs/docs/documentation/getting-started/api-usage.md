# Usage

## Getting a Token

Mealie supports long-live api tokens in the user frontend. These can be created on the `/user/profile/api-tokens` page.

## Key Components

### Exploring Your Local API
On your local installation you can access interactive API documentation that provides `curl` examples and expected results. This allows you to easily test and interact with your API to identify places to include your own functionality. You can visit the documentation at `http://<your-mealie-site>/docs` or see the example at the [Demo Site](https://demo.mealie.io/docs).

### Meal Plan Ordering

Meal plan entries have a `position` that determines their order within a day, starting at zero. By default, `GET /api/households/mealplans` returns entries ordered by date and then position. Without ordering parameters, both are sorted ascending.

You can pass `orderDirection=desc` to reverse this order, or use `orderBy` and the other [advanced ordering](#advanced-ordering) parameters to choose your own sort. These parameters only change the order of the results, they do not change the saved positions.

To reorder your household's entries or move them between days, you can use `PUT /api/households/mealplans/reorder`. The request contains a list of dates, each with its meal plan entry IDs in the desired order. For example:

```json
[
  {"date": "2026-10-20", "entryIds": [103, 101]},
  {"date": "2026-10-21", "entryIds": [102, 104]}
]
```

If October 20 contains entries `101`, `102`, and `103`, and October 21 contains `104`, this moves entry `102` to October 21 and places `103` before `101` on October 20. These are meal plan entry IDs, not recipe IDs. Dates outside the request are left unchanged.

Successful requests return `204 No Content`. An empty request or repeated dates or IDs returns `422`. If the IDs do not match your household's entries on the supplied dates, the API returns `409`. Fetch those days again before retrying.

New meal entries are placed after the last entry of the same meal type. If there are none, Mealie uses the meal type order: breakfast, lunch, dinner, side, snack, drink, dessert. This also applies when changing an entry's date through the regular update endpoint. Existing entries keep their relative order.

### Extras
#### Recipe Extras
Recipes extras are a key feature of the Mealie API. They allow you to create custom json key/value pairs within a recipe to reference from 3rd part applications. You can use these keys to contain information to trigger automation or custom messages to relay to your desired device.

For example you could add `{"message": "Remember to thaw the chicken"}` to a recipe and use the webhooks built into mealie to send that message payload to a destination to be processed.

#### Shopping List and Food Extras
Similarly to recipes, extras are supported on shopping lists, shopping list items, and foods. At this time they are only accessible through the API. Extras for these objects allow for rich integrations between the Mealie shopping list and your favorite list manager, such as Todoist, Trello, or any other list manager with an API.

To keep shopping lists in sync, for instance, you can store your Trello list id on your Mealie shopping list: <br />
`{"trello_list_id": "5abbe4b7ddc1b351ef961414"}`

Now if an update is made to your shopping list, you know which Trello list also needs to be updated. Similarly, you can also keep track of individual cards on your Trello list by storing data on shopping list items: <br />
`{"trello_card_id": "bab414bde415cd715efb9361"}`

Sometimes you may want to exclude certain foods from syncing to your external list, such as water, so you can add a custom property to your "water" food: <br />
`{"trello_exclude_food": "true"}`

You can combine your custom data definitions with our Event Subscriptions API, enabling you to keep your external list up-to-date in real time.

### Pagination and Filtering
Most document types share a uniform pagination and filtering API (e.g. `GET /api/recipes`). These allow you to filter by an arbitrary combination of criteria and return only a certain number of documents (i.e. a single "page" of documents).

#### Pagination
The pagination API allows you to limit how many documents you return in each call. This is important when serving data to an application, as you don't want to wait for a huge payload every time you load a page. You may also not want to render all documents at once, opting to render only a few at a time.

The `perPage` parameter tells Mealie how many documents to return (this is similar to `LIMIT` in SQL). If you want to keep fetching more data in batches, first determine your batch size (in other words: how many documents you want per-page), then make additional calls by changing the `page` parameter. If your `perPage` size is 30, then page 1 will return the first 30 documents, page 2 will return the next 30 documents, etc.

Many applications will keep track of the query and adjust the page parameter appropriately, but some applications can't do this, or a particular implementation may make this difficult. The response includes pagination guides to help you find the next page and previous page. Here is a sample response:
```json
{
  "page": 2,
  "per_page": 5,
  "total": 23,
  "total_pages": 5,
  "data": [...],
  "next": "/recipes?page=3&per_page=5&order_by=name&order_direction=asc",
  "previous": "/recipes?page=1&per_page=5&order_by=name&order_direction=asc"
}
```
Notice that the route does not contain the baseurl (e.g. `https://mymealieapplication.com/api`).

There are a few shorthands available to reduce the number of calls for certain common requests:

- if you want to return _all_ results, effectively disabling pagination, set `perPage = -1` (and fetch the first page)
- if you want to fetch the _last_ page, set `page = -1`

#### Filtering
The `queryFilter` parameter enables fine-grained control over your query. You can filter by any combination of attributes connected by logical operators (`AND`, `OR`). You can also group attributes together using parenthesis. For string, date, or datetime literals, you should surround them in double quotes (e.g. `"Pasta Fagioli"`). If there are no spaces in your literal (such as dates) the API will probably parse it correctly, but it's recommended that you use quotes anyway.

Here are several examples of filters. These filter strings are not surrounded in quotes for ease of reading, but they are _strings_, so they will probably be in quotes in your language.

##### Simple Filters
Here is an example of a filter to find a recipe with the name "Pasta Fagioli": <br>
`name = "Pasta Fagioli"`

This filter will find all recipes created on or after a particular date: <br>
`createdAt >= "2021-02-22"`

> **_NOTE:_**  The API uses Python's [dateutil parser](https://dateutil.readthedocs.io/en/stable/parser.html), which parses many different date/datetime formats.

This filter will find all units that have `useAbbreviation` disabled: <br>
`useAbbreviation = false`

This filter will find all foods that are not named "carrot": <br>
`name <> "carrot"`

##### Keyword Filters
The API supports many SQL keywords, such as `IS NULL` and `IN`, as well as their negations (e.g. `IS NOT NULL` and `NOT IN`).

Here is an example of a filter that returns all shopping list items without a food: <br>
`foodId IS NULL`

This filter will find all recipes that don't start with the word "Test": <br>
`name NOT LIKE "Test%"`

> **_NOTE:_** for more information on this, [check out the SQL "LIKE" operator](https://www.w3schools.com/sql/sql_like.asp)

This filter will find all recipes that have particular slugs: <br>
`slug IN ["pasta-fagioli", "delicious-ramen"]`

##### Placeholder Keywords
You can use placeholders to insert dynamic values as opposed to static values. Currently the only supported placeholder keyword is `$NOW`, to insert the current date/time.

`$NOW` can optionally be paired with basic offsets. Here is an example of a filter which gives you recipes not made within the past 30 days: <br>
`lastMade <= "$NOW-30d"`

Supported offset operations include:

- `-` for subtracting a time (i.e. in the past)
- `+` for adding a time (i.e. in the future)

Supported offset intervals include:

- `y` for years
- `m` for months
- `d` for days
- `H` for hours
- `M` for minutes
- `S` for seconds

Note that intervals are _case sensitive_ (e.g. `s` is an invalid interval).

##### Nested Property filters
When querying tables with relationships, you can filter properties on related tables. For instance, if you want to query all recipes owned by a particular user: <br>
`user.username = "SousChef20220320"`

This timeline event filter will return all timeline events for recipes that were created after a particular date: <br>
`recipe.createdAt >= "2023-02-25"`

This recipe filter will return all recipes that contain a particular set of tags: <br>
`tags.name CONTAINS ALL ["Easy", "Cajun"]`

##### Compound Filters
You can combine multiple filter statements using logical operators (`AND`, `OR`).

This filter will only return recipes named "Pasta Fagioli" or "Grandma's Brisket": <br>
`name = "Pasta Fagioli" OR name = "Grandma's Brisket"`

This filter will return all recipes created before a particular date, except for the one named "Ultimate Vegan Ramen Recipe With Miso Broth": <br>
`createdAt < "January 2nd, 2014" AND name <> "Ultimate Vegan Ramen Recipe With Miso Broth"`

This filter will return three particular recipes: <br>
`name = "Pasta Fagioli" OR name = "Grandma's Brisket" OR name = "Ultimate Vegan Ramen Recipe With Miso Broth"`

##### Advanced Filters
You can have multiple filter groups combined by logical operators. You can define a filter group with parenthesis.

Here's a filter that will find all recipes updated between two particular times, but exclude the "Pasta Fagioli" recipe: <br>
`(updatedAt > "2022-07-17T15:47:00Z" AND updatedAt < "2022-07-17T15:50:00Z") AND name <> "Pasta Fagioli"`

#### Advanced Ordering
Pagination supports `orderBy`, `orderByNullPosition`, and `orderDirection` params to change how you want your query results to be ordered. These can be fine-tuned for more advanced use-cases.

##### Order By
The pagination `orderBy` attribute allows you to sort your query results by a particular attribute. Sometimes, however, [you may want to sort by more than one attribute](https://www.w3schools.com/sql/sql_orderby.asp). This can be achieved by passing a comma-separated string to the `orderBy` parameter. For instance, if you want to sort recipes by their last made datetime, then by their created datetime, you can pass the following `orderBy` string: <br>
`lastMade, createdAt`

Similar to the standard SQL `ORDER BY` logic, your attribute orders will be applied sequentially. In the above example, *first* recipes will be sorted by `lastMade`, *then* any recipes with an identical `lastMade` value are sorted by `createdAt`. In addition, standard SQL rules apply when handling results with null values (such as when joining related tables). You can apply the `NULLS FIRST` and `NULLS LAST` SQL expressions by setting the `orderByNullPosition` to "first" or "last". If left empty, the default SQL behavior is applied, [which is different depending on which database you're using](https://learnsql.com/blog/how-to-order-rows-with-nulls/).

##### Order Direction
The query will be ordered in ascending or descending order, depending on what you pass to the pagination `orderDirection` param. You can either specify "asc" or "desc".

When sorting by multiple attributes, if you *also* want one or more of those sorts to be different directions, you can specify them with a colon. For instance, if, like our previous example, say you want to sort by `lastMade` and `createdAt`. However, this time, you want to sort by `lastMade` ascending, but `createdAt` descending. You could pass this `orderBy` string: <br>
`lastMade:asc, createdAt:desc`

In the above example, whatever you pass to `orderDirection` will be ignored. If, however, you only specify the direction on one attribute, all other attributes will use the `orderDirection` value.

Consider this `orderBy` string: <br>
`lastMade:asc, createdAt, slug`

And this `orderDirection` value: <br>
`desc`

This will result in a recipe query where all recipes are sorted by `lastMade` ascending, then `createdAt` descending, and finally `slug` descending.

Similar to query filters, when querying tables with relationships, you can order by properties on related tables. For instance, if you want to query all foods with labels, sorted by label name, you could use this `orderBy` value: <br>
`label.name`
