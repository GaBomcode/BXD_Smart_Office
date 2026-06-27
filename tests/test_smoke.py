from database.init_db import init_database
from services.profile_service import ProfileService
from services.task_service import TaskService


def test_database_seed() -> None:
    init_database()
    assert len(ProfileService().get_staff()) >= 8
    assert len(ProfileService().get_work_codes()) >= 7


def test_task_service_stats() -> None:
    init_database()
    stats = TaskService().get_stats()
    assert "total" in stats
