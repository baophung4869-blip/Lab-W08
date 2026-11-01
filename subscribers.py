"""
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
Module định nghĩa các lớp Subscriber lắng nghe sự kiện từ thiết bị giảng dạy.
"""
from typing import Any, List, Sequence
from events import (
    DeviceAlertEventArgs,
    DeviceStatusChangedEventArgs,
)


class ConsoleNotificationService:
    """Dịch vụ hiển thị thông báo cảnh báo thiết bị trực tiếp ra màn hình Console."""

    def handle_alert(self, sender: Any, e: DeviceAlertEventArgs) -> None:
        """Xử lý sự kiện cảnh báo và in thông tin chi tiết ra màn hình."""
        print(f"[{e.severity.value}] {e.device_id}: {e.message}")


class DeviceAuditLogger:
    """Dịch vụ ghi nhận lịch sử thay đổi trạng thái của các thiết bị."""

    def __init__(self) -> None:
        self._entries: List[str] = []

    @property
    def entries(self) -> Sequence[str]:
        """Trả về danh sách lịch sử thay đổi ở dạng chỉ đọc (tuple)."""
        return tuple(self._entries)

    def handle_status_changed(
        self, sender: Any, e: DeviceStatusChangedEventArgs
    ) -> None:
        """Ghi lại bản ghi nhật ký mỗi khi thiết bị thay đổi trạng thái."""
        timestamp = e.changed_at.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"{timestamp}: {e.device_id}, "
            f"{e.old_status.value} -> {e.new_status.value}"
        )
        self._entries.append(log_entry)