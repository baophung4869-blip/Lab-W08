"""
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
Module định nghĩa các ngoại lệ tùy chỉnh cho hệ thống thiết bị.
"""

class InvalidDeviceReadingException(Exception):
    """
    Ngoại lệ phát sinh khi chỉ số đọc được từ thiết bị (như pin, tín hiệu) 
    nằm ngoài khoảng hợp lệ cho phép (0 - 100).
    """

    def __init__(self, device_id: str, invalid_value: int):
        message = f"Thiết bị '{device_id}' có chỉ số không hợp lệ: {invalid_value}. Chỉ số phải nằm trong khoảng 0-100."
        super().__init__(message)
        self._device_id = device_id
        self._invalid_value = invalid_value

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def invalid_value(self) -> int:
        return self._invalid_value