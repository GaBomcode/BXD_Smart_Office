from typing import Any
from repositories.base_repository import BaseRepository


class ProfileRepository(BaseRepository):
    def list_staff(self) -> list[dict[str, Any]]:
        return self.fetch_all("SELECT * FROM staff ORDER BY id")

    def list_work_codes(self) -> list[dict[str, Any]]:
        return self.fetch_all("SELECT * FROM work_codes WHERE active=1 ORDER BY axis, code")

    def list_kpi_rules(self) -> list[dict[str, Any]]:
        return self.fetch_all("SELECT * FROM kpi_rules ORDER BY point DESC")

    def add_staff(self, full_name: str, position: str, field: str, can_receive_task: int = 1) -> int:
        return self.execute("INSERT INTO staff(full_name, position, field, can_receive_task) VALUES(?,?,?,?)", (full_name, position, field, can_receive_task))

    def add_work_code(self, data: dict[str, Any]) -> int:
        return self.execute("""
            INSERT INTO work_codes(code, axis, group_name, task_name, output_product, frequency, level, point, coefficient)
            VALUES(:code, :axis, :group_name, :task_name, :output_product, :frequency, :level, :point, :coefficient)
        """, data)
