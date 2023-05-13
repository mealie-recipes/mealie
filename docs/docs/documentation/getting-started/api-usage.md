# Usage

## Getting a Token

Mealie supports long-live api tokens in the user frontend. These can be created on the `/user/profile/api-tokens` page.

## Key Components

### Exploring Your Local API
On your local installation you can access interactive API documentation that provides `curl` examples and expected results. This allows you to easily test and interact with your API to identify places to include your own functionality. You can visit the documentation at `http://<your-mealie-site>/docs` or see the example at the [Demo Site](https://demo.mealie.io/docs).

### Extras
#### Recipe Extras
Recipes extras are a key feature of the Mealie API. They allow you to create custom json key/value pairs within a recipe to reference from 3rd part applications. You can use these keys to contain information to trigger automation or custom messages to relay to your desired device.

For example you could add `{"message": "Remember to thaw the chicken"}` to a recipe and use the webhooks built into mealie to send that message payload to a destination to be processed.

#### Shopping List and Food Extras
Similarly to recipes, extras are supported on shopping lists, shopping list items, and foods. At this time they are only accessible through the API. Extras for these objects allow for rich integrations between the Mealie shopping list and your favorite list manager, such as Alexa, ToDoist, Trello, or any other list manager with an API.

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

##### Nested Property filters
When querying tables with relationships, you can filter properties on related tables. For instance, if you want to query all recipes owned by a particular user: <br>
`user.username = "SousChef20220320"`

This timeline event filter will return all timeline events for recipes that were created after a particular date: <br>
`recipe.createdAt >= "2023-02-25"`

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
