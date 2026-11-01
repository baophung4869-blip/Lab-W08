"""
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
Module định nghĩa các kiểu liệt kê, cấu trúc dữ liệu sự kiện và cơ chế EventSource/EventView
đảm bảo chỉ Publisher mới có quyền phát sinh sự kiện, chống đăng ký trùng và cô lập lỗi.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Generic, List, TypeVar

TEventArgs = TypeVar("TEventArgs")


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


class EventSource(Generic[TEventArgs]):
    """
    Nguồn sự kiện nội bộ của Publisher.
    Quản lý danh sách subscriber, chống đăng ký trùng lặp và cô lập ngoại lệ khi invoke.
    """

    def __init__(self) -> None:
        self._handlers: List[Callable[[Any, TEventArgs], None]] = []

    def subscribe(self, handler: Callable[[Any, TEventArgs], None]) -> None:
        """Đăng ký một hàm xử lý sự kiện (bỏ qua nếu handler đã tồn tại)."""
        if handler is None:
            raise ValueError("Handler đăng ký không được null.")
        if handler not in self._handlers:
            self._handlers.append(handler)

    def unsubscribe(self, handler: Callable[[Any, TEventArgs], None]) -> None:
        """Hủy đăng ký một hàm xử lý sự kiện."""
        if handler in self._handlers:
            self._handlers.remove(handler)

    def invoke(self, sender: Any, args: TEventArgs) -> None:
        """
        Kích hoạt tất cả các handler đã đăng ký.
        Cô lập ngoại lệ của từng subscriber để đảm bảo tính ổn định của chuỗi sự kiện.
        """
        for handler in list(self._handlers):
            try:
                handler(sender, args)
            except Exception as ex:
                handler_name = getattr(handler, "__qualname__", str(handler))
                print(
                    f"[EventError] Subscriber '{handler_name}' gặp lỗi khi xử lý sự kiện: {ex}"
                )


class EventView(Generic[TEventArgs]):
    """
    Giao diện sự kiện công khai cho phép mã bên ngoài đăng ký (+=) và hủy đăng ký (-=),
    nhưng hoàn toàn ngăn chặn việc tự ý phát sinh sự kiện (không có invoke).
    """

    def __init__(self, source: EventSource[TEventArgs]) -> None:
        self._source = source

    def __iadd__(
        self, handler: Callable[[Any, TEventArgs], None]
    ) -> "EventView[TEventArgs]":
        self._source.subscribe(handler)
        return self

    def __isub__(
        self, handler: Callable[[Any, TEventArgs], None]
    ) -> "EventView[TEventArgs]":
        self._source.unsubscribe(handler)
        return self