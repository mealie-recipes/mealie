from db.tinydb.tinydb_setup import TinyDatabase

db = TinyDatabase()

test_object = {"name": "dan", "job": "programmer"}
test_object_2 = {"name": "jennifer", "job": "programmer"}
test_object_3 = {"name": "steve", "job": "programmer"}


db.recipes.delete("jennifer")
db.recipes.delete("dan")
db.recipes.save(test_object)
db.recipes.save(test_object_2)
db.recipes.update_doc("dan", test_object_3)
