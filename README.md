# Review Studio 0.2

Ứng dụng cục bộ tạo video review bán hàng, xuất MP4 H.264/AAC 720×1280 và giữ âm thanh gốc.

**[Tải bản 0.2](https://github.com/tinhot24h/Dungx/raw/refs/heads/main/ReviewStudio-v0.2.zip)** · Xem `HUONG_DAN.txt` để cài và chạy.

## Bản 0.2 có gì mới?

- Hai mẫu: **Mỹ phẩm hồng** (khung bo góc, nhiều lớp viền, bóng sáng và ngôi sao) và **Gia dụng xanh** (chữ trắng/vàng có viền, nền xanh có họa tiết nhẹ).
- Hòa chân video vào nền bằng lớp màu alpha tăng dần theo đường cong mềm. Không phải bộ lọc blur làm nhòe video.
- Chỉnh điểm bắt đầu hòa nền, chiều cao vùng chuyển, độ đục cuối; chỉnh vị trí khung chữ độc lập.
- Chỉnh màu nền, độ bóng khung hồng, phóng to và căn video theo chiều dọc.
- Giao diện ba cột, điều khiển phát/dừng, thanh tua và tắt/bật tiếng xem trước.
- Tự lưu thiết kế trong trình duyệt; clip không được lưu vào trình duyệt. Có thể để trống CTA.
- Lớp đồ họa PNG dùng chung giữa xem trước và xuất, cùng font và cách xuống dòng. Đường viền, baseline chữ giữa trình duyệt và FFmpeg có thể chênh nhẹ.

## Chạy

Cần Python 3.11+, FFmpeg/FFprobe với libx264/drawtext. Font DejaVu Sans và giấy phép đã kèm trong `assets/`. Không cần pip, npm hoặc API key.

```sh
python3 launch.py
```

Windows: mở `START_WINDOWS.bat`. macOS/Linux: chạy lệnh trên trong thư mục đã giải nén. Trình duyệt tự mở cổng loopback 8000. Đặt `PORT` để đổi cổng; `--no-browser` để không mở trình duyệt. Health: `curl --fail http://127.0.0.1:8000/health`.

## Sử dụng

1. Tải clip tối đa 100 MB / 180 giây. Ưu tiên clip gốc chưa có khung chữ.
2. Chọn mẫu, nhập nội dung, chỉnh hòa nền và căn hình.
3. Nhấn Xuất MP4 rồi tải về. Nếu sửa thiết kế khi đang xuất, file vẫn dùng thiết kế tại thời điểm bấm Xuất.

Video được phóng để phủ toàn khung 9:16, có thể cắt bớt hình khi khác tỷ lệ. Không thêm viền đen để giữ nguyên toàn hình như bản cũ. Video dưới lớp nền vẫn tồn tại, vì vậy giảm độ đục sẽ để lộ hình phía dưới. Chữ và watermark có sẵn trên clip không bị xóa.

## Giới hạn

Chưa có ghép nhiều clip, giọng đọc AI hay tự đăng TikTok. Mẫu là đồ họa được dựng lại theo phong cách tham khảo, không phải trích xuất nguyên khung của video mẫu. Chưa đóng gói EXE hoặc kèm Python/FFmpeg.

Chỉ phục vụ cục bộ: chưa có xác thực, giới hạn hàng đợi hay tự dọn ổ đĩa. Tệp tải lên và kết quả nằm trong `.local/` được Git bỏ qua. Trạng thái tác vụ trong RAM, mất sau khi khởi động lại; tải kết quả trước khi dừng. Khi ứng dụng đã dừng, có thể xóa `.local/` nếu đã giữ các kết quả cần thiết.

## Kiểm tra và đóng gói

```sh
python3 -m unittest discover -s tests -v
python3 build_package.py
```

API: `POST /upload` nhận byte video; `POST /design` nhận thiết kế trả PNG overlay và layout chữ; `POST /render` nhận thiết kế kèm `id`; `GET /jobs/<id>` theo dõi; `GET /download/<id>` lấy MP4.

Đã kiểm tra bằng Chromium trên Linux: hai mẫu, chỉnh slider, xuất/tải, lưu thiết kế, bố cục 390px và không có lỗi JavaScript. Đã thử xuất cả hai clip tham khảo khoảng 28 giây, xác minh kích thước, thời lượng, âm thanh và giải mã toàn bộ. Chưa chạy trực tiếp trên Windows/macOS.
