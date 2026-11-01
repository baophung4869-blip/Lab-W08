"""
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
Chương trình chính kiểm thử hệ thống quản lý sự kiện thiết bị giảng dạy (Lab W08).
"""
import sys
from coordinator import DeviceMonitoringCoordinator
from devices import (
    AirConditionerRemote,
    ProjectorRemote,
    WirelessMicrophone,
)
from events import AlertSeverity, DeviceAlertEventArgs, DeviceStatus
from exceptions import InvalidDeviceReadingException
from subscribers import (
    ConsoleNotificationService,
    DeviceAuditLogger,
    FilteredAlertSubscriber,
    MaintenanceService,
)

# Đảm bảo hiển thị tiếng Việt UTF-8 trên Windows PowerShell/Console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_simulation() -> None:
    print("=" * 72)
    print("CHƯƠNG TRÌNH KIỂM THỬ HỆ THỐNG SỰ KIỆN THIẾT BỊ GIẢNG DẠY (LAB W08)")
    print("=" * 72)

    # 1. Khởi tạo các thiết bị giảng dạy (Publishers)
    projector_remote = ProjectorRemote("PRJ-101", "Điều khiển máy chiếu Epson", initial_battery=80)
    ac_remote = AirConditionerRemote("AC-202", "Điều khiển điều hòa Daikin", assigned_room="D3-301")
    wireless_mic = WirelessMicrophone("MIC-303", "Micro không dây Shure", initial_battery=85, initial_signal=90)

    devices = [projector_remote, ac_remote, wireless_mic]

    # 2. Khởi tạo các dịch vụ giám sát (Subscribers)
    notification_service = ConsoleNotificationService()
    audit_logger = DeviceAuditLogger()
    maintenance_service = MaintenanceService()

    # 3. Khởi tạo FilteredAlertSubscriber với Delegate & Callback
    critical_only_subscriber = FilteredAlertSubscriber(
        alert_filter=lambda alert: alert.severity == AlertSeverity.CRITICAL,
        action=lambda alert: print(
            f"   >>> [CALLBACK LỌC CRITICAL] {alert.device_id} - {alert.message}"
        ),
    )
    for dev in devices:
        dev.alert_raised += critical_only_subscriber.handle_alert

    # 4. Điều phối đăng ký qua DeviceMonitoringCoordinator
    coordinator = DeviceMonitoringCoordinator(
        devices=devices,
        notification_service=notification_service,
        audit_logger=audit_logger,
        maintenance_service=maintenance_service,
    )
    coordinator.subscribe()
    # Gọi subscribe() lần 2 để kiểm tra chống đăng ký trùng lặp
    coordinator.subscribe()

    print("\n--- [KỊCH BẢN 1] THAY ĐỔI TRẠNG THÁI THIẾT BỊ ---")
    projector_remote.change_status(DeviceStatus.BORROWED)
    # Gọi lại cùng trạng thái BORROWED -> Không phát sinh thêm sự kiện
    projector_remote.change_status(DeviceStatus.BORROWED)
    wireless_mic.change_status(DeviceStatus.BORROWED)
    ac_remote.change_status(DeviceStatus.UNDER_MAINTENANCE)
    projector_remote.change_status(DeviceStatus.AVAILABLE)
    print("Đã cập nhật trạng thái các thiết bị thành công (kiểm tra trong Audit Log).")

    print("\n--- [KỊCH BẢN 2] CẬP NHẬT MỨC PIN ĐIỀU KHIỂN MÁY CHIẾU ---")
    print("* Hạ pin PRJ-101 xuống 15% (Warning):")
    projector_remote.update_battery_level(15)
    print("* Hạ pin PRJ-101 xuống 12% (Cùng vùng Warning -> Không phát lại cảnh báo):")
    projector_remote.update_battery_level(12)
    print("* Hạ pin PRJ-101 xuống 0% (Critical):")
    projector_remote.update_battery_level(0)

    print("\n--- [KỊCH BẢN 3] TRẠNG THÁI PHẢN HỒI CỦA ĐIỀU KHIỂN ĐIỀU HÒA ---")
    print("* AC-202 chuyển sang không phản hồi (Critical):")
    ac_remote.update_response_state(False)
    print("* AC-202 tiếp tục cập nhật không phản hồi (Không lặp lại cảnh báo):")
    ac_remote.update_response_state(False)

    print("\n--- [KỊCH BẢN 4] CẬP NHẬT PIN VÀ TÍN HIỆU MICRO KHÔNG DÂY ---")
    print("* Hạ pin MIC-303 xuống 25% (< 30% -> Warning):")
    wireless_mic.update_battery_level(25)
    print("* Hạ tín hiệu MIC-303 xuống 35% (< 40% -> Warning):")
    wireless_mic.update_signal_quality(35)
    print("* Mất hoàn toàn tín hiệu MIC-303 (0% -> Critical):")
    wireless_mic.update_signal_quality(0)

    print("\n--- [KỊCH BẢN 5] KIỂM TRA NGOẠI LỆ & TÍNH ỔN ĐỊNH CỦA EVENT ---")
    try:
        print("* Thử cập nhật mức pin không hợp lệ (150%) cho PRJ-101:")
        projector_remote.update_battery_level(150)
    except InvalidDeviceReadingException as ex:
        print(f"[Bắt ngoại lệ thành công] {ex} (Mã TB: {ex.device_id}, Giá trị lỗi: {ex.invalid_value})")

    try:
        print("* Thử phát sinh sự kiện trực tiếp từ bên ngoài (kiểm tra tính đóng gói):")
        projector_remote.alert_raised.invoke(projector_remote, None)  # type: ignore
    except AttributeError as ex:
        print(f"[Bảo vệ đóng gói thành công] Mã bên ngoài không thể gọi invoke(): {ex}")

    def faulty_subscriber(sender: object, e: DeviceAlertEventArgs) -> None:
        raise RuntimeError("Lỗi kết nối máy chủ gửi email giả lập!")

    print("* Đăng ký một subscriber bị lỗi và kiểm tra cô lập ngoại lệ:")
    wireless_mic.alert_raised += faulty_subscriber
    wireless_mic.update_battery_level(0)
    wireless_mic.alert_raised -= faulty_subscriber

    print("\n--- [KỊCH BẢN 6] HỦY ĐĂNG KÝ (UNSUBSCRIBE / DISPOSE) ---")
    coordinator.dispose()
    for dev in devices:
        dev.alert_raised -= critical_only_subscriber.handle_alert
    print("* Đã gọi coordinator.dispose(). Thử đổi trạng thái và cập nhật lại thiết bị:")
    ac_remote.update_response_state(True)
    ac_remote.update_response_state(False)
    wireless_mic.change_status(DeviceStatus.AVAILABLE)
    print("-> Không có thông báo hoặc bản ghi mới nào phát sinh sau khi hủy đăng ký.")

    print("\n" + "=" * 72)
    print(f"LỊCH SỬ THAY ĐỔI TRẠNG THÁI (DeviceAuditLogger - Tổng: {len(audit_logger.entries)}):")
    for idx, entry in enumerate(audit_logger.entries, start=1):
        print(f"  {idx}. {entry}")

    print("-" * 72)
    print(f"DANH SÁCH YÊU CẦU BẢO TRÌ (MaintenanceService - Tổng: {len(maintenance_service.requests)}):")
    for idx, req in enumerate(maintenance_service.requests, start=1):
        print(f"  {idx}. {req}")
    print("=" * 72)


if __name__ == "__main__":
    run_simulation()
    