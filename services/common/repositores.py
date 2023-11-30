from common.entites import Entity
from dataclasses import asdict
from common.tables import Base
from sqlalchemy.orm import Session


class Repository:
    def save(self, obj: Entity) -> None:
        pass

    def update(self, obj: Entity) -> None:
        pass


class SQLRepository(Repository):
    TABLE: Base = None

    def __init__(self, engine, *args, **kwargs) -> None:
        self._engine = engine

        super().__init__(*args, **kwargs)

    def save(self, obj: Entity) -> None:
        obj_data = asdict(obj=obj)

        with Session(self._engine) as session:
            table_obj = self.TABLE(**obj_data)
            session.add(table_obj)
            session.commit()

    def update(self, obj: Entity) -> None:
        obj_data = asdict(obj=obj)

        with Session(self._engine) as session:
            table_obj = session.query(self.TABLE).populate_existing().with_for_update().filter(self.TABLE.id == obj.id).first()
            for attr, value in obj_data.items():
                setattr(table_obj, attr, value)

            session.add(table_obj)
            session.commit()

    @property
    def collection(self):
        return self._db[self.COLLECTION_NAME]
