"""
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
Module định nghĩa các kiểu liệt kê, cấu trúc dữ liệu sự kiện và cơ chế EventHandler.
"""
from datetime import datetime
from enum import Enum


class DeviceStatus(Enum):
    """Trạng thái hiện tại của thiết bị giảng dạy."""
    AVAILABLE = "Available"
    BORROWED = "Borrowed"
    UNDER_MAINTENANCE = "UnderMaintenance"


class AlertSeverity(Enum):
    """Mức độ nghiêm trọng của cảnh báo phát sinh từ thiết bị."""
    INFORMATION = "Information"
    WARNING = "Warning"
    CRITICAL = "Critical"


class DeviceStatusChangedEventArgs:
    """Dữ liệu đi kèm sự kiện thay đổi trạng thái thiết bị."""

    def __init__(
        self,
        device_id: str,
        old_status: DeviceStatus,
        new_status: DeviceStatus,
        changed_at: datetime,
    ):
        self._device_id = device_id
        self._old_status = old_status
        self._new_status = new_status
        self._changed_at = changed_at

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def old_status(self) -> DeviceStatus:
        return self._old_status

    @property
    def new_status(self) -> DeviceStatus:
        return self._new_status

    @property
    def changed_at(self) -> datetime:
        return self._changed_at


class DeviceAlertEventArgs:
    """Dữ liệu đi kèm sự kiện cảnh báo thiết bị."""

    def __init__(
        self,
        device_id: str,
        message: str,
        severity: AlertSeverity,
        occurred_at: datetime,
    ):
        self._device_id = device_id
        self._message = message
        self._severity = severity
        self._occurred_at = occurred_at

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def message(self) -> str:
        return self._message

    @property
    def severity(self) -> AlertSeverity:
        return self._severity

    @property
    def occurred_at(self) -> datetime:
        return self._occurred_at