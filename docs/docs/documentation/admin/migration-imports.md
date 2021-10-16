# Migration

## Chowdown
To migrate recipes from a Chowdown
 
  1. Download the code repository as a .zip file
  2. Upload the .zip file in the Chowdown section in Mealie
  3. Select import on the newly available migration. 

## Nextcloud Recipes
Nextcloud recipes can be imported from a zip file that contains the data stored in Nextcloud. The zip file can be uploaded from the frontend or placed in the data/migrations/nextcloud directory. See the example folder structure below to ensure your recipes are able to be imported. 

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

## CSV Import
Imports lists of URLs from a CSV file, with optional tags and categories.

The CSV file should be pipe (`|`) separated and contain one url per row. Tags and categories should be comma separated and are optional.

```
links|tags|categories
https://www.smoking-meat.com/september-24-2015-smoked-pork-tenderloin|bbq,smoking,american|main
https://bbqpitboys.com/smoked-whiskey-cheeseburgers/
```

The ZIP file should contain the CSV files in a flat directory. The files can end in any `.*sv` pattern.

```
recipes.zp
  ├── recipes_american.csv
  └── recipes_bbq.tsv
```
