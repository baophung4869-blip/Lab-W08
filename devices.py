"""
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
Module định nghĩa lớp cơ sở trừu tượng TeachingDevice và các thiết bị dẫn xuất.
"""
from abc import ABC
from datetime import datetime
from typing import Optional
from events import (
    AlertSeverity,
    DeviceAlertEventArgs,
    DeviceStatus,
    DeviceStatusChangedEventArgs,
    EventSource,
    EventView,
)
from exceptions import InvalidDeviceReadingException


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

        # Nguồn phát sự kiện nội bộ (chỉ lớp này và lớp con được quyền kích hoạt)
        self._status_changed_source = EventSource[DeviceStatusChangedEventArgs]()
        self._alert_raised_source = EventSource[DeviceAlertEventArgs]()

        # Giao diện công khai chỉ cho phép += và -= từ bên ngoài
        self._status_changed_view = EventView(self._status_changed_source)
        self._alert_raised_view = EventView(self._alert_raised_source)

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> DeviceStatus:
        return self._status

    @property
    def status_changed(self) -> EventView[DeviceStatusChangedEventArgs]:
        """Sự kiện công khai khi trạng thái thay đổi (chỉ hỗ trợ += và -=)."""
        return self._status_changed_view

    @status_changed.setter
    def status_changed(self, value: EventView[DeviceStatusChangedEventArgs]) -> None:
        if value is not self._status_changed_view:
            raise AttributeError("Không được phép gán đè trực tiếp đối tượng sự kiện.")

    @property
    def alert_raised(self) -> EventView[DeviceAlertEventArgs]:
        """Sự kiện công khai khi phát sinh cảnh báo (chỉ hỗ trợ += và -=)."""
        return self._alert_raised_view

    @alert_raised.setter
    def alert_raised(self, value: EventView[DeviceAlertEventArgs]) -> None:
        if value is not self._alert_raised_view:
            raise AttributeError("Không được phép gán đè trực tiếp đối tượng sự kiện.")

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
        self._status_changed_source.invoke(self, e)

    def _on_alert_raised(self, e: DeviceAlertEventArgs) -> None:
        """Kích hoạt sự kiện alert_raised; lớp dẫn xuất có thể mở rộng."""
        self._alert_raised_source.invoke(self, e)


class ProjectorRemote(TeachingDevice):
    """Lớp đại diện cho điều khiển máy chiếu."""

    def __init__(self, device_id: str, name: str, initial_battery: int = 100) -> None:
        super().__init__(device_id, name)
        if not (0 <= initial_battery <= 100):
            raise InvalidDeviceReadingException(self.id, initial_battery)
        self._battery_level = initial_battery

    @property
    def battery_level(self) -> int:
        return self._battery_level

    @staticmethod
    def _get_battery_zone(level: int) -> Optional[AlertSeverity]:
        """Xác định vùng cảnh báo ứng với mức pin (None là vùng an toàn >= 20%)."""
        if level == 0:
            return AlertSeverity.CRITICAL
        if level < 20:
            return AlertSeverity.WARNING
        return None

    def update_battery_level(self, new_level: int) -> None:
        """
        Cập nhật mức pin (0-100) và chỉ phát cảnh báo khi chuyển vùng trạng thái
        (tránh phát cảnh báo lặp lại khi vẫn ở cùng một vùng).
        """
        if not (0 <= new_level <= 100):
            raise InvalidDeviceReadingException(self.id, new_level)

        old_zone = self._get_battery_zone(self._battery_level)
        new_zone = self._get_battery_zone(new_level)
        self._battery_level = new_level

        # Không phát sinh cảnh báo nếu vẫn nằm trong cùng một vùng trạng thái
        if new_zone is None or new_zone == old_zone:
            return

        if new_zone == AlertSeverity.CRITICAL:
            self._raise_alert(
                "Điều khiển máy chiếu đã cạn sạch pin (0%).",
                AlertSeverity.CRITICAL,
            )
        elif new_zone == AlertSeverity.WARNING:
            self._raise_alert(
                f"Mức pin điều khiển máy chiếu xuống thấp ({new_level}% < 20%).",
                AlertSeverity.WARNING,
            )
class AirConditionerRemote(TeachingDevice):
    """Lớp đại diện cho điều khiển điều hòa."""

    def __init__(
        self,
        device_id: str,
        name: str,
        assigned_room: str,
        is_responsive: bool = True,
    ) -> None:
        super().__init__(device_id, name)
        if not assigned_room or not assigned_room.strip():
            raise ValueError("Tên phòng được phân công (assigned_room) không được để trống.")
        self._assigned_room = assigned_room.strip()
        self._is_responsive = is_responsive

    @property
    def assigned_room(self) -> str:
        return self._assigned_room

    @property
    def is_responsive(self) -> bool:
        return self._is_responsive

    def update_response_state(self, is_responsive: bool) -> None:
        """
        Cập nhật trạng thái phản hồi của điều khiển điều hòa.
        Chỉ phát cảnh báo Critical khi chuyển từ phản hồi (True) sang không phản hồi (False).
        """
        was_responsive = self._is_responsive
        self._is_responsive = is_responsive

        if was_responsive and not is_responsive:
            self._raise_alert(
                f"Điều khiển điều hòa tại phòng {self._assigned_room} mất phản hồi.",
                AlertSeverity.CRITICAL,
            )
class WirelessMicrophone(TeachingDevice):
    """Lớp đại diện cho micro không dây."""

    def __init__(
        self,
        device_id: str,
        name: str,
        initial_battery: int = 100,
        initial_signal: int = 100,
    ) -> None:
        super().__init__(device_id, name)
        if not (0 <= initial_battery <= 100):
            raise InvalidDeviceReadingException(self.id, initial_battery)
        if not (0 <= initial_signal <= 100):
            raise InvalidDeviceReadingException(self.id, initial_signal)

        self._battery_level = initial_battery
        self._signal_quality = initial_signal

    @property
    def battery_level(self) -> int:
        return self._battery_level

    @property
    def signal_quality(self) -> int:
        return self._signal_quality

    @staticmethod
    def _get_battery_zone(level: int) -> Optional[AlertSeverity]:
        """Xác định vùng cảnh báo cho mức pin của micro (dưới 30% là Warning, 0% là Critical)."""
        if level == 0:
            return AlertSeverity.CRITICAL
        if level < 30:
            return AlertSeverity.WARNING
        return None

    @staticmethod
    def _get_signal_zone(quality: int) -> Optional[AlertSeverity]:
        """Xác định vùng cảnh báo cho chất lượng tín hiệu (dưới 40% là Warning, 0% là Critical)."""
        if quality == 0:
            return AlertSeverity.CRITICAL
        if quality < 40:
            return AlertSeverity.WARNING
        return None

    def update_battery_level(self, new_level: int) -> None:
        """Cập nhật mức pin (0-100) của micro và phát cảnh báo khi chuyển vùng."""
        if not (0 <= new_level <= 100):
            raise InvalidDeviceReadingException(self.id, new_level)

        old_zone = self._get_battery_zone(self._battery_level)
        new_zone = self._get_battery_zone(new_level)
        self._battery_level = new_level

        if new_zone is None or new_zone == old_zone:
            return

        if new_zone == AlertSeverity.CRITICAL:
            self._raise_alert(
                "Micro không dây đã cạn sạch pin (0%).",
                AlertSeverity.CRITICAL,
            )
        elif new_zone == AlertSeverity.WARNING:
            self._raise_alert(
                f"Mức pin micro không dây xuống thấp ({new_level}% < 30%).",
                AlertSeverity.WARNING,
            )

    def update_signal_quality(self, new_quality: int) -> None:
        """Cập nhật chất lượng tín hiệu (0-100) của micro và phát cảnh báo khi chuyển vùng."""
        if not (0 <= new_quality <= 100):
            raise InvalidDeviceReadingException(self.id, new_quality)

        old_zone = self._get_signal_zone(self._signal_quality)
        new_zone = self._get_signal_zone(new_quality)
        self._signal_quality = new_quality

        if new_zone is None or new_zone == old_zone:
            return

        if new_zone == AlertSeverity.CRITICAL:
            self._raise_alert(
                "Micro không dây mất hoàn toàn tín hiệu (0%).",
                AlertSeverity.CRITICAL,
            )
        elif new_zone == AlertSeverity.WARNING:
            self._raise_alert(
                f"Chất lượng tín hiệu micro không dây yếu ({new_quality}% < 40%).",
                AlertSeverity.WARNING,
            )