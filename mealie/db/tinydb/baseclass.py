from tinydb import Query, TinyDB, where


class StoreBase:
    def __init__(self) -> None:
        self.store: TinyDB
        self.primary_key: str

    def save(self, document: dict) -> str:
        data = self.store.search(
            Query()[self.primary_key] == document[self.primary_key]
        )

        if data != []:
            raise Exception(
                f"Cannot Save, Primary Key: {self.primary_key} already exists"
            )
        else:
            self.store.insert(document)
            return document

    def delete(self, document_primary_key: str):
        self.store.remove(where(self.primary_key) == document_primary_key)

    def get_all(self) -> list:
        return self.store.all()

    def get(self, value: str, key: str = None, limit: int = None) -> list or dict:
        """Retrieves an entry from the database matching the key/value provided.
        If no key is provided the classes primary_key will be used instead

        Args: \n
            key (str, optional): Key to match against. Defaults to None. \n
            value (str, optional): Value the key should contain. Defaults to None. \n
            limit (int, optional): The limit of returned objects If 1 a single item is returned. If None all objects are returned. Defaults to None. \n

        Returns:
            list or dict: a List if limit is greater than 1
        """

        if key == None:
            key = self.primary_key

        data = self.store.search(Query()[key] == value)

        if limit == 1:
            return data[0]
        if limit:
            return data[:limit]
        else:
            return data

    def update_doc(self, id, document):
        data: dict = self.get(id, self.primary_key, limit=1)

        if data:
            if data[self.primary_key] == document[self.primary_key]:
                data.update(document)
                return document["slug"]
            else:
                self.delete(id)
                self.save(document)
                return document["slug"]

        elif not data:
            raise Exception(
                f"Document'{document[self.primary_key]}' does not exists and cannot be updated. "
            )
