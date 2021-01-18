# Migration

### Chowdown

In the Admin page on the in the Migration section you can provide a URL for a repo hosting a [Chowdown](https://github.com/clarklab/chowdown) repository and Mealie will pull the images and recipes from the instance and automatically import them into the database. Due to the nature of the yaml format you may have mixed results but you should get an error report of the recipes that had errors and will need to be manually added. Note that you can only import the repo as a whole. You cannot import individual recipes. 

We'd like to support additional migration paths. [See open issues.](https://github.com/hay-kot/mealie/issues)

### Nextcloud Recipes
Nextcloud recipes can be imported from either a zip file the contains the data stored in Nextcloud. The zip file can be uploaded from the frontend or placed in the data/migrations/Nextcloud directory. See the example folder structure below to ensure your recipes are able to be imported. 

```
nextcloud_recipes.zip
  ├── recipe_1
  │   ├── recipe.json
  │   ├── full.jpg
  │   └── thumb.jpg
  ├── recipe_2
  │   ├── recipe.json
  │   └── full.jpg
  └── recipe_3
      └── recipe.json
```

**Currently Proposed Are:**
- Open Eats