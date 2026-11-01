"""
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
Module định nghĩa các lớp Subscriber lắng nghe sự kiện từ thiết bị giảng dạy
và cơ chế lọc thông báo bằng Delegate/Callback.
"""
from typing import Any, Callable, List, Sequence
from events import (
    AlertSeverity,
    DeviceAlertEventArgs,
    DeviceStatusChangedEventArgs,
)

# Định nghĩa kiểu Delegate tự định nghĩa cho chính sách lọc thông báo
AlertFilter = Callable[[DeviceAlertEventArgs], bool]


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


class MaintenanceService:
    """Dịch vụ tự động khởi tạo yêu cầu bảo trì khi nhận cảnh báo mức Critical."""

    def __init__(self) -> None:
        self._requests: List[str] = []

    @property
    def requests(self) -> Sequence[str]:
        """Trả về danh sách các yêu cầu bảo trì ở dạng chỉ đọc (tuple)."""
        return tuple(self._requests)

    def handle_critical_alert(
        self, sender: Any, e: DeviceAlertEventArgs
    ) -> None:
        """Lọc cảnh báo mức Critical và thêm yêu cầu bảo trì vào danh sách."""
        if e.severity != AlertSeverity.CRITICAL:
            return

        request = f"Maintenance request for {e.device_id}: {e.message}"
        self._requests.append(request)


class FilteredAlertSubscriber:
    """
    Subscriber sử dụng delegate AlertFilter và callback Action để lọc
    và xử lý các sự kiện cảnh báo theo chính sách tùy biến.
    """

    def __init__(
        self,
        alert_filter: AlertFilter,
        action: Callable[[DeviceAlertEventArgs], None],
    ) -> None:
        if alert_filter is None:
            raise ValueError("Delegate bộ lọc (alert_filter) không được null.")
        if action is None:
            raise ValueError("Callback hành động (action) không được null.")

        self._filter = alert_filter
        self._action = action

    def handle_alert(self, sender: Any, e: DeviceAlertEventArgs) -> None:
        """Kiểm tra điều kiện qua delegate filter trước khi kích hoạt callback action."""
        if self._filter(e):
            self._action(e)