# Review Studio 0.4

Công cụ cục bộ dựng video review 9:16 và biên tập lời tiếng Việt từ văn bản tiếng Trung.

**[Tải bản 0.4](https://github.com/tinhot24h/Dungx/raw/refs/heads/main/ReviewStudio-v0.4.zip)** · Cài/chạy: `HUONG_DAN.txt`.

## Hai không gian làm việc

**Dựng video:** giao diện chia nguồn, canvas và bảng thuộc tính. Nhập X/Y/W/H theo pixel thật trên canvas 720×1280. X/Y là góc trên bên trái; nút căn giữa ngang/dọc cho khung, từng hộp chữ và video. Giữ thanh trượt kèm ô số cho các thông số như độ đục/vùng hòa nền. Cỡ chữ 12–144 px, có thể nhập trực tiếp 90 px. W/H video liên kết 9:16 mặc định; bỏ chọn để kéo giãn hình.

**Dịch & biên tập AI:** dán văn bản Trung → OpenAI trả bản dịch sát nghĩa, bản viết lại và điểm cần kiểm chứng. Chọn Review / Tin tức / Chia sẻ mẹo / Giới thiệu sản phẩm; chọn giọng văn, xưng hô và mục tiêu 15/30/60/90 giây hoặc giữ đủ ý. Sửa hai bản, sao chép hoặc tải TXT UTF-8 để tạo MP3 ở công cụ ngoài. Thời lượng đọc chỉ ước tính 2,8 tiếng/giây. Có thể bôi đen một đoạn tối đa 600 ký tự rồi đưa vào khung nội dung video.

**Chưa có tự trích lời từ video, OCR, tạo giọng đọc AI hoặc tạo MP3.** Nguồn dịch hiện là văn bản do bạn dán vào, tối đa 8.000 ký tự.

## OpenAI: kết nối và chi phí

Ở tab Dịch & biên tập AI, mở Kết nối OpenAI và nhập API key trong ứng dụng, không gửi key trong chat. Key nhập tại giao diện chỉ dùng trong phiên, không lưu vào thiết kế, localStorage hoặc file; tải lại trang cần nhập lại. Có thể thay bằng biến máy chủ `REVIEW_OPENAI_KEY` hoặc `OPENAI_API_KEY`. Model mặc định `gpt-4.1-mini`, có thể đổi trong giao diện hoặc qua `OPENAI_MODEL`; model cần hỗ trợ Responses API và Structured Outputs.

Chỉ khi bấm Dịch & viết lại, ứng dụng gửi văn bản/cấu hình tới `https://api.openai.com/v1/responses` bằng HTTPS, với `store:false`. Không gửi clip hoặc PNG tới OpenAI. Phí API tính riêng với gói ChatGPT và theo tài khoản/key của bạn. Cần Internet tới `api.openai.com`.

Prompt yêu cầu giữ dữ kiện, không tự quy đổi giá hay bịa trải nghiệm/công dụng. Đây là hướng dẫn cho mô hình, không thay thế việc đối chiếu của người dùng. Lỗi key, quyền model, hết hạn mức và mất mạng hiển thị riêng; lỗi không xóa kịch bản trước đó.

## Các chức năng dựng video được giữ

- Nền một màu hoặc chuyển hai màu, tám màu gợi ý, lớp hòa nền alpha mềm.
- Sáu khung dựng sẵn; đổi màu, viền, độ đục, độ bóng của khung hồng. Kính trong là lớp bán trong suốt, không phải blur hậu cảnh.
- Khung PNG từ máy (tối đa 5 MB, 4096 px/cạnh, 8 triệu điểm ảnh). Giữ tỷ lệ và căn giữa trong hộp; PNG động chỉ lấy hình đầu.
- Tiêu đề/nội dung chỉnh riêng font, màu, cỡ, vị trí, độ rộng, căn dòng, khoảng dòng và viền. Sáu font từ ba họ Sans/Serif/Mono, có nét thường/đậm, kèm giấy phép trong `assets/`.
- Kéo trực tiếp bốn lớp; bộ điều khiển phát/tua/tắt tiếng xem trước. Khung/chữ không buộc di chuyển cùng nhau.
- MP4 H.264/AAC 720×1280, giữ tiếng gốc, không thêm CTA. Clip tối đa 100 MB / 180 giây.

## Chạy và cập nhật

Cần Python 3.11+ và FFmpeg/FFprobe có libx264/drawtext. Không cài pip/npm hoặc SDK OpenAI; dùng thư viện chuẩn Python. Python/FFmpeg không kèm ZIP, đây chưa phải EXE.

```sh
python3 launch.py
```

Windows mở `START_WINDOWS.bat`. macOS/Linux dùng lệnh trên trong thư mục giải nén. Trình duyệt tự mở cổng loopback 8000; `PORT` đổi cổng, `--no-browser` không tự mở trình duyệt. Health: `curl --fail http://127.0.0.1:8000/health`.

Dừng bản cũ, giải nén bản mới vào thư mục mới rồi chạy. Không cần cài lại Python/FFmpeg đã có. Nếu cùng trình duyệt/địa chỉ/cổng và chưa có thiết kế 0.4, ứng dụng chuyển bản lưu 0.3 từ % sang px. PNG thuộc thư mục cũ cần tải lại khi chuyển thư mục.

## Tọa độ và lưu dữ liệu

X tăng sang phải, Y tăng xuống dưới. X/Y của khung, video là cạnh trái/trên, không phải tâm; X/Y hộp chữ cũng vậy. Căn giữa hộp chữ đồng thời chọn căn dòng giữa. Khung/video có thể nằm một phần ngoài canvas; phần đó bị cắt khi xuất. Chữ vượt cạnh phải hoặc chiều cao canvas sẽ báo lỗi. Nền và khung dùng chung giữa xem trước/xuất; baseline và viền chữ có thể chênh nhẹ giữa trình duyệt và FFmpeg.

Thiết kế và văn bản AI lưu riêng trong localStorage; có nút xóa văn bản AI. Video/PNG/MP4 ở `.local/`, được Git/ZIP bỏ qua. Trạng thái tác vụ xuất ở RAM, mất khi máy chủ dừng: tải kết quả trước khi dừng. Chỉ xóa `.local/` sau khi ứng dụng đã dừng và đã giữ các tệp cần thiết.

Máy chủ chỉ chấp nhận Host/Origin cục bộ, không phục vụ triển khai công khai. Chưa có đăng nhập, dọn ổ đĩa hay giới hạn hàng đợi video. Chưa có ghép nhiều clip và tự đăng TikTok. Chữ/watermark trong nguồn không bị xóa.

## Kiểm tra và đóng gói

```sh
python3 -m unittest discover -s tests -v
node --check studio.js
node --check ai_ui.js
python3 build_package.py
```

Đã kiểm tra trên Linux/Chromium: số px/cỡ 90 px, căn giữa hai trục, W/H liên kết, kéo lớp, xuất khung dựng sẵn/PNG với âm thanh, lưu thiết kế và bố cục 390px. Luồng UI AI được kiểm tra bằng phản hồi giả lập: cấu hình phong cách/thời lượng, hai kết quả, copy/TXT, chuyển đoạn chọn, lỗi hạn mức và không lưu key. Unit test giả lập HTTP để kiểm tra request HTTPS, Responses API/JSON schema, `store:false`, thiếu key, từ chối phản hồi lỗi/dở dang và thông báo lỗi không lộ key.

**Chưa thử gọi OpenAI thật vì máy kiểm tra không có API key.** Cần nhập key có hạn mức API để kiểm tra bản dịch thực tế. Chưa chạy trực tiếp Windows/macOS.

API: `/upload`, `/frame-upload`, `/design`, `/render`, `/jobs/<id>`, `/download/<id>`, `/frames/<id>`, `/ai-status`, `/translate`. `/translate` nhận `source,style,tone,pronoun,duration,model` và `api_key` tùy chọn; trả `literal,script,notes,model`.
