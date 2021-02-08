# Migration

## Chowdown
To migrate recipes from a Chowdown 
  1. Download the code repository as a .zip file
  2. Upload the .zip file in the Chowdown section in Mealie
  3. Select import on the newly available migration. 

## Nextcloud Recipes
Nextcloud recipes can be imported from a zip file the contains the data stored in Nextcloud. The zip file can be uploaded from the frontend or placed in the data/migrations/nextcloud directory. See the example folder structure below to ensure your recipes are able to be imported. 

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
