"""
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
Module định nghĩa các kiểu liệt kê, cấu trúc dữ liệu sự kiện và cơ chế EventHandler.
"""
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