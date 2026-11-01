<!--
/****************/
Mã sinh viên: 20237303
Họ tên: Phùng Ngọc Bảo
/****************/
-->

# HỆ THỐNG GIÁM SÁT SỰ KIỆN THIẾT BỊ GIẢNG DẠY (LAB W08: DELEGATE & EVENT)

## 1. Thông tin sinh viên
* **Họ và tên:** Phùng Ngọc Bảo
* **Mã số sinh viên:** 20237303
* **Học phần:** Lập trình hướng đối tượng (MI4090)

## 2. Cấu trúc thư mục dự án
* `DESIGN.md`: Tài liệu phân tích Publisher, Subscriber, danh sách Event, dữ liệu đi kèm (`EventArgs`), sơ đồ lớp UML và câu trả lời cho 3 câu hỏi thiết kế cốt lõi.
* `exceptions.py`: Định nghĩa ngoại lệ nghiệp vụ `InvalidDeviceReadingException` khi chỉ số pin hoặc chất lượng tín hiệu nằm ngoài khoảng `0 - 100`.
* `events.py`: Định nghĩa các kiểu liệt kê (`DeviceStatus`, `AlertSeverity`), các lớp dữ liệu sự kiện bất biến (`DeviceStatusChangedEventArgs`, `DeviceAlertEventArgs`), và cơ chế quản lý sự kiện tách biệt giữa `EventSource` (nội bộ) và `EventView` (công khai).
* `devices.py`: Cài đặt lớp cơ sở trừu tượng `TeachingDevice` và các lớp thiết bị dẫn xuất (`ProjectorRemote`, `AirConditionerRemote`, `WirelessMicrophone`).
* `subscribers.py`: Cài đặt các dịch vụ nhận sự kiện (`ConsoleNotificationService`, `DeviceAuditLogger`, `MaintenanceService`) và bộ lọc thông báo bằng Delegate/Callback (`AlertFilter`, `FilteredAlertSubscriber`).
* `coordinator.py`: Cài đặt lớp điều phối tập trung `DeviceMonitoringCoordinator` hỗ trợ `subscribe()`, `unsubscribe()` và `dispose()`.
* `main.py`: Kịch bản kiểm thử toàn diện các tính năng nghiệp vụ và xử lý ngoại lệ.

## 3. Điểm nhấn thiết kế & Minh chứng phản biện cùng AI
1. **Bảo vệ quyền phát sinh sự kiện (Commit 9 - `fix`):** Tách `EventSource` (lưu nội bộ trong `TeachingDevice` để gọi `invoke`) và `EventView` (công khai qua `@property`, chỉ hỗ trợ toán tử `+=` và `-=`). Ngăn chặn hoàn toàn mã bên ngoài tự ý kích hoạt sự kiện của thiết bị.
2. **Chống cảnh báo lặp theo vùng trạng thái (Commit 11 - `fix`):** Cải tiến `ProjectorRemote` và `WirelessMicrophone` kiểm tra vùng trạng thái (`NORMAL`, `WARNING`, `CRITICAL`), chỉ phát cảnh báo khi thiết bị chuyển sang vùng cảnh báo mới, tránh gây nhiễu hệ thống khi chỉ số biến động nhỏ trong cùng một vùng.
3. **Chống đăng ký trùng lặp & Cô lập ngoại lệ giữa các Subscriber (Commit 18 - `fix`):** Nâng cấp `EventSource` để bỏ qua các handler đăng ký trùng và bọc lời gọi từng subscriber trong khối `try...except`, đảm bảo nếu một subscriber gặp lỗi runtime thì các subscriber còn lại vẫn nhận được sự kiện bình thường.

## 4. Hướng dẫn chạy chương trình
Mở Terminal / PowerShell tại thư mục gốc của dự án và chạy lệnh:

```powershell
python main.py