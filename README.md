# Review Studio 0.3

Công cụ cục bộ thiết kế video review bán hàng, xuất MP4 H.264/AAC 720×1280 và giữ âm thanh gốc.

**[Tải bản 0.3](https://github.com/tinhot24h/Dungx/raw/refs/heads/main/ReviewStudio-v0.3.zip)** · Hướng dẫn chi tiết: `HUONG_DAN.txt`.

## Các tính năng mới

- **Nền:** tám màu gợi ý, chọn màu bất kỳ, nền một màu hoặc chuyển hai màu; chỉnh vị trí và độ dài vùng hòa nền, độ đục 0–100%.
- **Khung:** sáu kiểu Hồng bóng, Kính trong, Viền đôi, Tối giản, Neon, Thiệp; hoặc không dùng khung. Có thể đổi màu bên trong/viền, độ đục, kích thước và vị trí khung. Kính trong là lớp bán trong suốt, không phải blur hậu cảnh.
- **Khung PNG từ máy:** PNG tĩnh có alpha, tối đa 5 MB, 4096 px mỗi cạnh và 8 triệu điểm ảnh. Giữ nguyên tỷ lệ ảnh trong hộp khung, căn giữa; chỉnh hộp để phù hợp thiết kế. PNG được chuẩn hóa về một ảnh RGBA. Với PNG động, chỉ lấy khung hình đầu.
- **Tiêu đề và nội dung độc lập:** sáu lựa chọn font từ ba họ Sans/Serif/Mono (thường/đậm), màu chữ, cỡ 12–72 px, căn trái/giữa/phải, vị trí, độ rộng hộp, khoảng dòng và màu/độ dày viền. Hỗ trợ Enter xuống dòng. Tự ngắt dòng theo độ rộng font; báo lỗi nếu chữ vượt chiều cao khung hình.
- **Video:** thu nhỏ/phóng to 50–200%, dịch ngang và dọc; phần trống dùng màu nền chính. Video khác tỷ lệ được cắt về 9:16 trước khi đặt lên nền.
- **Kéo trực tiếp:** chọn lớp video/khung/tiêu đề/nội dung dưới bản xem trước rồi kéo. Khung và chữ không bị buộc di chuyển cùng nhau.
- **Bỏ CTA:** không còn ô lời kêu gọi hành động và không vẽ CTA trong file xuất.
- Tự lưu thiết kế trong trình duyệt. Font được đóng gói kèm, không tải font từ Internet. Nền và khung dùng chung giữa xem trước và xuất; viền/baseline chữ có thể chênh nhẹ giữa trình duyệt và FFmpeg.

## Chạy

Cần Python 3.11+ và FFmpeg/FFprobe có libx264/drawtext. Không cần pip/npm, API key hay dịch vụ ngoài. Phông DejaVu và giấy phép ở `assets/`.

```sh
python3 launch.py
```

Windows: mở `START_WINDOWS.bat`. macOS/Linux: chạy lệnh trên trong thư mục đã giải nén. Trình duyệt tự mở cổng loopback 8000. Đặt `PORT` để đổi cổng hoặc thêm `--no-browser` để không tự mở trình duyệt. Health check: `curl --fail http://127.0.0.1:8000/health`.

## Quy trình

1. Chọn clip tối đa 100 MB / 180 giây. Ưu tiên clip gốc chưa có chữ.
2. Chọn mẫu hồng/xanh làm điểm bắt đầu. Mở từng tab Nền / Khung / Tiêu đề / Nội dung / Video để chỉnh.
3. Khung PNG: tab Khung → tải tệp PNG. Đổi vị trí và kích thước; sau đó đặt chữ vào vùng trống của ảnh.
4. Để kéo lớp, chọn đúng lớp trong hộp dưới bản xem trước. Đặt lại về Tắt để thao tác cuộn bình thường trên điện thoại.
5. Xuất MP4, chờ sẵn sàng và tải về. File dùng thiết kế tại thời điểm bấm Xuất.

Thay đổi khung không tự di chuyển chữ. Nội dung dài hoặc chữ lớn có thể tràn khỏi khung trang trí: xem trước rồi tăng khung hoặc giảm chữ. Xuất bị chặn nếu chữ tràn khỏi khung hình. Xóa/sửa chữ hoặc watermark đã có trong clip gốc không được hỗ trợ.

## Cập nhật và dữ liệu

Dừng bản cũ, giải nén bản mới vào thư mục mới, chạy trình khởi động. Không cần cài lại Python/FFmpeg. Không chép đè lên phiên đang chạy.

Thiết kế lưu bằng khóa trình duyệt riêng cho bản 0.3. Video, PNG tải lên và kết quả nằm trong `.local/`, được Git và gói ZIP bỏ qua. Khi chuyển sang thư mục/máy mới, tải lại PNG nếu thiết kế báo mất khung. Trạng thái tác vụ ở RAM, mất khi khởi động lại: hãy tải MP4 cần giữ trước khi dừng. Chỉ xóa `.local/` sau khi ứng dụng đã dừng và đã lưu các kết quả cần giữ.

## Giới hạn và xác minh

Ứng dụng cục bộ chưa có xác thực, giới hạn hàng đợi hoặc dọn dữ liệu tự động. Chưa có ghép nhiều clip, giọng đọc AI, xuất EXE hay tự đăng TikTok. Python/FFmpeg không nằm trong ZIP. Chưa chạy thử trực tiếp trên Windows/macOS.

Đã kiểm tra trên Linux/Chromium: sáu khung xuất có âm thanh, PNG trong suốt xem trước/xuất, font Sans/Serif/Mono, xuống dòng, căn chữ, màu nền chuyển, kéo cả bốn lớp, di chuyển/thu nhỏ video, lưu thiết kế và bố cục 390px. Kiểm tra pixel xác nhận video di chuyển đúng chỗ và để lộ màu nền đã chọn. Unit test kiểm tra alpha mềm, khung/chữ độc lập, ngắt dòng tiếng Việt, vị trí giới hạn và từ chối thông số không hợp lệ.

```sh
python3 -m unittest discover -s tests -v
python3 build_package.py
```

API: `POST /upload` (byte video); `POST /frame-upload` (byte PNG); `POST /design` (JSON thiết kế → PNG nền/khung và layout chữ); `POST /render` (thiết kế + id video); `GET /jobs/<id>`; `GET /download/<id>`. PNG tùy chỉnh được phục vụ bằng `GET /frames/<id>`.
