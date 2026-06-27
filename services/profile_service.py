from typing import Any
from repositories.profile_repository import ProfileRepository
from core.logger import get_logger

logger = get_logger(__name__)


class ProfileService:
    def __init__(self) -> None:
        self.repo = ProfileRepository()

    def get_staff(self) -> list[dict[str, Any]]:
        return self.repo.list_staff()

    def get_work_codes(self) -> list[dict[str, Any]]:
        return self.repo.list_work_codes()

    def get_kpi_rules(self) -> list[dict[str, Any]]:
        return self.repo.list_kpi_rules()
