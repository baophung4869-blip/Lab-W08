"""
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
Module định nghĩa lớp cơ sở trừu tượng TeachingDevice và các thiết bị dẫn xuất.
"""
from abc import ABC
from datetime import datetime
from events import (
    AlertSeverity,
    DeviceAlertEventArgs,
    DeviceStatus,
    DeviceStatusChangedEventArgs,
    EventHandler,
)


class TeachingDevice(ABC):
    """
    Lớp cơ sở trừu tượng cho các thiết bị giảng dạy.
    Đóng vai trò Publisher phát hiện và công bố các sự kiện trạng thái và cảnh báo.
    """

    def __init__(self, device_id: str, name: str) -> None:
        if not device_id or not device_id.strip():
            raise ValueError("Mã thiết bị (id) không được để trống.")
        if not name or not name.strip():
            raise ValueError("Tên thiết bị (name) không được để trống.")

        self._id = device_id.strip()
        self._name = name.strip()
        self._status = DeviceStatus.AVAILABLE

        self.status_changed = EventHandler[DeviceStatusChangedEventArgs]()
        self.alert_raised = EventHandler[DeviceAlertEventArgs]()

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> DeviceStatus:
        return self._status

    def change_status(self, new_status: DeviceStatus) -> None:
        """
        Cập nhật trạng thái thiết bị và phát sinh sự kiện nếu trạng thái thay đổi.
        """
        if new_status == self._status:
            return

        old_status = self._status
        self._status = new_status

        self._on_status_changed(
            DeviceStatusChangedEventArgs(
                device_id=self._id,
                old_status=old_status,
                new_status=new_status,
                changed_at=datetime.now(),
            )
        )

    def _raise_alert(self, message: str, severity: AlertSeverity) -> None:
        """Phương thức bảo vệ để lớp thiết bị hoặc lớp dẫn xuất phát cảnh báo."""
        self._on_alert_raised(
            DeviceAlertEventArgs(
                device_id=self._id,
                message=message,
                severity=severity,
                occurred_at=datetime.now(),
            )
        )

    def _on_status_changed(self, e: DeviceStatusChangedEventArgs) -> None:
        """Kích hoạt sự kiện status_changed; lớp dẫn xuất có thể mở rộng."""
        self.status_changed.invoke(self, e)

    def _on_alert_raised(self, e: DeviceAlertEventArgs) -> None:
        """Kích hoạt sự kiện alert_raised; lớp dẫn xuất có thể mở rộng."""
        self.alert_raised.invoke(self, e)