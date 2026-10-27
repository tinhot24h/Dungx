# Review Studio

Web app cục bộ tạo video review bán hàng từ clip có sẵn: khung tiêu đề, mô tả, CTA, màu nền; xuất MP4 H.264/AAC 720×1280, giữ âm thanh gốc. Không tự tạo cảnh, giọng đọc AI hoặc đăng TikTok.

## Chạy

Yêu cầu Python 3.11+, FFmpeg/FFprobe có `libx264` và `drawtext`, phông DejaVu Sans đã kèm tại `assets/`. Không cần cài pip/npm hay API key.

```sh
cd /duong-dan/toi/ReviewStudio
python3 launch.py
```

Ứng dụng phục vụ cổng 8000 trên loopback. Có thể đổi cổng bằng biến `PORT`. Kiểm tra sức khỏe: `curl --fail http://127.0.0.1:8000/health`.

Chọn clip tối đa 100 MB / 180 giây, điền nội dung rồi xuất. Máy chủ xử lý từng tác vụ xuất lần lượt; mỗi tác vụ tối đa 10 phút. Clip gốc được giữ trọn khung trong vùng phía trên, có viền đen khi khác tỉ lệ. Mô tả tối đa 6 dòng, tiêu đề tối đa 3 dòng.

Tệp tải lên và kết quả nằm trong `.local/` (Git bỏ qua). Trạng thái tác vụ ở RAM, khởi động lại sẽ mất trạng thái tải về. Tự xóa `.local/` khi đã lưu kết quả và không còn tác vụ đang chạy. Đây là công cụ phát triển cục bộ, chưa có xác thực, dọn dữ liệu tự động hoặc giới hạn hàng đợi; cần bổ sung trước khi triển khai công khai.

## Kiểm chứng chức năng

Tải clip bằng `POST /upload` (body là byte video), dùng `id` trả về gọi `POST /render` với JSON `id,title,body,cta,color`. Thăm dò `GET /jobs/<id>` đến `state=done`, tải `GET /download/<id>` và dùng FFprobe kiểm tra kích thước, thời lượng, luồng âm thanh. Health check chỉ xác minh máy chủ HTTP, không thay thế thử xuất video.

## Gói tải về

Xem `HUONG_DAN.txt` để cài Python/FFmpeg và chạy trên Windows, macOS hoặc Linux. Windows: nhấp đúp `START_WINDOWS.bat`. Font và giấy phép font được đóng gói kèm; Python và FFmpeg cần cài riêng.
