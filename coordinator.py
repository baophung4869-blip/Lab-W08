"""
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
Module định nghĩa lớp điều phối đăng ký và hủy đăng ký sự kiện tập trung.
"""
from typing import Iterable, List
from devices import TeachingDevice
from subscribers import (
    ConsoleNotificationService,
    DeviceAuditLogger,
    MaintenanceService,
)


class DeviceMonitoringCoordinator:
    """
    Lớp điều phối quản lý việc đăng ký (+=) và hủy đăng ký (-=) tập trung
    giữa danh sách các thiết bị (Publisher) và các dịch vụ giám sát (Subscriber).
    """

    def __init__(
        self,
        devices: Iterable[TeachingDevice],
        notification_service: ConsoleNotificationService,
        audit_logger: DeviceAuditLogger,
        maintenance_service: MaintenanceService,
    ) -> None:
        if devices is None:
            raise ValueError("Danh sách thiết bị (devices) không được null.")
        if notification_service is None:
            raise ValueError("Dịch vụ thông báo (notification_service) không được null.")
        if audit_logger is None:
            raise ValueError("Dịch vụ ghi nhật ký (audit_logger) không được null.")
        if maintenance_service is None:
            raise ValueError("Dịch vụ bảo trì (maintenance_service) không được null.")

        self._devices: List[TeachingDevice] = list(devices)
        self._notification_service = notification_service
        self._audit_logger = audit_logger
        self._maintenance_service = maintenance_service
        self._is_subscribed = False

    def subscribe(self) -> None:
        """
        Đăng ký các handler cần thiết cho từng thiết bị.
        Chặn đăng ký trùng nếu đã ở trạng thái đăng ký.
        """
        if self._is_subscribed:
            return

        for device in self._devices:
            device.status_changed += self._audit_logger.handle_status_changed
            device.alert_raised += self._notification_service.handle_alert
            device.alert_raised += self._maintenance_service.handle_critical_alert

        self._is_subscribed = True

    def unsubscribe(self) -> None:
        """Hủy đúng các đăng ký đã tạo trước đó."""
        if not self._is_subscribed:
            return

        for device in self._devices:
            device.status_changed -= self._audit_logger.handle_status_changed
            device.alert_raised -= self._notification_service.handle_alert
            device.alert_raised -= self._maintenance_service.handle_critical_alert

        self._is_subscribed = False

    def dispose(self) -> None:
        """Giải phóng tài nguyên điều phối bằng cách gọi unsubscribe()."""
        self.unsubscribe()

    def __enter__(self) -> "DeviceMonitoringCoordinator":
        """Hỗ trợ cú pháp with (tương đương IDisposable trong C#)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Tự động gọi dispose() khi thoát khỏi khối with."""
        self.dispose()
        