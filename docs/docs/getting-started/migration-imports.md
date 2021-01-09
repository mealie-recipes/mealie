# Migration

### Chowdown

In the Admin page on the in the Migration section you can provide a URL for a repo hosting a [Chowdown](https://github.com/clarklab/chowdown) repository and Mealie will pull the images and recipes from the instance and automatically import them into the database. Due to the nature of the yaml format you may have mixed results but you should get an error report of the recipes that had errors and will need to be manually added. Note that you can only import the repo as a whole. You cannot import individual recipes. 

We'd like to support additional migration paths. [See open issues.](https://github.com/hay-kot/mealie/issues)

**Currently Proposed Are:**

- NextCloud Recipes
- Open Eats