import uvicorn
from piccolo.table import create_db_tables_sync
from piccolo_admin.endpoints import create_admin
from starlette.routing import Mount, Router

from common.tables import Gym, GymClass, GymClassBook


def migrate() -> None:
    create_db_tables_sync(Gym, GymClass, GymClassBook, if_not_exists=True)


admin = create_admin([Gym, GymClass, GymClassBook])


router = Router([
    Mount(path="/admin/", app=admin),
])


if __name__ == '__main__':
    migrate()
    uvicorn.run(router, host='0.0.0.0', port=8000)
