<!--
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
-->

# TÀI LIỆU THIẾT KẾ HỆ THỐNG (LAB W08: DELEGATE & EVENT)

## 1. Xác định Publisher và Subscriber

### 1.1. Publisher (Nguồn phát sự kiện)
* **`TeachingDevice` (Lớp cơ sở trừu tượng):** Quản lý trạng thái chung và cung cấp hai sự kiện cốt lõi là `status_changed` và `alert_raised`.
* **Các lớp thiết bị dẫn xuất:**
  * `ProjectorRemote` (Điều khiển máy chiếu): Phát cảnh báo khi mức pin giảm thấp (< 20%) hoặc cạn pin (0%).
  * `AirConditionerRemote` (Điều khiển điều hòa): Phát cảnh báo nghiêm trọng khi chuyển từ trạng thái có phản hồi sang mất phản hồi.
  * `WirelessMicrophone` (Micro không dây): Phát cảnh báo khi mức pin thấp (< 30%), chất lượng tín hiệu kém (< 40%), hoặc khi pin/tín hiệu bằng 0%.

### 1.2. Subscriber (Thành phần đăng ký nhận sự kiện)
* **`ConsoleNotificationService`:** Lắng nghe sự kiện cảnh báo (`alert_raised`) để hiển thị thông báo trực tiếp ra màn hình Console.
* **`DeviceAuditLogger`:** Lắng nghe sự kiện thay đổi trạng thái (`status_changed`) để ghi nhận lịch sử chuyển đổi trạng thái thiết bị theo thời gian.
* **`MaintenanceService`:** Lắng nghe sự kiện cảnh báo (`alert_raised`), lọc các cảnh báo có mức độ nghiêm trọng (`Critical`) để tự động khởi tạo yêu cầu bảo trì.
* **`FilteredAlertSubscriber`:** Thành phần lắng nghe tùy biến sử dụng delegate `AlertFilter` và callback `Action` để lọc và xử lý thông báo theo chính sách linh hoạt.

---

## 2. Danh sách các Event cần thiết

1. **`status_changed` (`EventHandler[DeviceStatusChangedEventArgs]`):**
   * Phát sinh khi phương thức `change_status(new_status)` được gọi với trạng thái mới khác trạng thái hiện tại.
   * Trạng thái mới bắt buộc phải được cập nhật xong trước khi phát sinh sự kiện.
2. **`alert_raised` (`EventHandler[DeviceAlertEventArgs]`):**
   * Phát sinh từ bên trong lớp `TeachingDevice` hoặc các lớp con thông qua phương thức bảo vệ `_raise_alert(message, severity)` khi phát hiện bất thường về pin, tín hiệu hoặc khả năng phản hồi.

---

## 3. Dữ liệu đi kèm mỗi Event (EventArgs)

1. **`DeviceStatusChangedEventArgs`:**
   * `device_id` (`str`): Mã định danh của thiết bị thay đổi trạng thái.
   * `old_status` (`DeviceStatus`): Trạng thái trước khi thay đổi (`Available`, `Borrowed`, `UnderMaintenance`).
   * `new_status` (`DeviceStatus`): Trạng thái mới sau khi cập nhật.
   * `changed_at` (`datetime`): Thời điểm xảy ra sự thay đổi trạng thái.

2. **`DeviceAlertEventArgs`:**
   * `device_id` (`str`): Mã định danh của thiết bị phát cảnh báo.
   * `message` (`str`): Nội dung chi tiết của cảnh báo.
   * `severity` (`AlertSeverity`): Mức độ cảnh báo (`Information`, `Warning`, `Critical`).
   * `occurred_at` (`datetime`): Thời điểm phát sinh cảnh báo.
---

## 4. Sơ đồ lớp UML (Kiến trúc tổng quát)

```mermaid
classDiagram
    class TeachingDevice {
        <<abstract>>
        +str id
        +str name
        +DeviceStatus status
        +Event status_changed
        +Event alert_raised
        +change_status(DeviceStatus new_status)
        #_raise_alert(str message, AlertSeverity severity)
        #_on_status_changed(DeviceStatusChangedEventArgs e)
        #_on_alert_raised(DeviceAlertEventArgs e)
    }

    class ProjectorRemote {
        +int battery_level
        +update_battery_level(int new_level)
    }

    class AirConditionerRemote {
        +str assigned_room
        +bool is_responsive
        +update_response_state(bool is_responsive)
    }

    class WirelessMicrophone {
        +int battery_level
        +int signal_quality
        +update_battery_level(int new_level)
        +update_signal_quality(int new_quality)
    }

    class ConsoleNotificationService {
        +handle_alert(sender, DeviceAlertEventArgs e)
    }

    class DeviceAuditLogger {
        +Sequence~str~ entries
        +handle_status_changed(sender, DeviceStatusChangedEventArgs e)
    }

    class MaintenanceService {
        +Sequence~str~ requests
        +handle_critical_alert(sender, DeviceAlertEventArgs e)
    }

    class FilteredAlertSubscriber {
        +handle_alert(sender, DeviceAlertEventArgs e)
    }

    class DeviceMonitoringCoordinator {
        +subscribe()
        +unsubscribe()
        +dispose()
    }

    TeachingDevice <|-- ProjectorRemote
    TeachingDevice <|-- AirConditionerRemote
    TeachingDevice <|-- WirelessMicrophone

    DeviceMonitoringCoordinator --> TeachingDevice : đăng ký/hủy đăng ký
    DeviceMonitoringCoordinator --> ConsoleNotificationService : điều phối
    DeviceMonitoringCoordinator --> DeviceAuditLogger : điều phối
    DeviceMonitoringCoordinator --> MaintenanceService : điều phối