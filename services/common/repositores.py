from common.entites import Entity
from dataclasses import asdict


class Repository:
    def save(self, obj: Entity) -> None:
        pass

    def update(self, obj: Entity) -> None:
        pass


class MongoRepository(Repository):
    COLLECTION_NAME: str = ""

    def __init__(self, db, *args, **kwargs) -> None:
        self._db = db

        super().__init__(*args, **kwargs)

    def save(self, obj: Entity) -> None:
        obj_data = asdict(obj=obj)

        self.collection.insert_one(obj_data)

    def update(self, obj: Entity) -> None:
        self.collection.update_one({"id": obj.id}, {"$set": asdict(obj)})

    @property
    def collection(self):
        return self._db[self.COLLECTION_NAME]
