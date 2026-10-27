# Review Studio 0.5

Dựng video review 9:16, tạo câu lệnh dùng trên AI web hoặc dịch qua Gemini/OpenAI API.

**[Tải bản 0.5](https://github.com/tinhot24h/Dungx/raw/refs/heads/main/ReviewStudio-v0.5.zip)** · Cài/chạy: `HUONG_DAN.txt`.

## Chọn cách dịch

| Chế độ | Cần key? | Cách hoạt động |
| --- | --- | --- |
| **Thủ công — mặc định** | Không | Tool ghép nguồn + phong cách thành câu lệnh. Bạn sao chép sang Gemini/ChatGPT web, lấy câu trả lời rồi dán trở lại. Tool không gọi API. Dịch vụ web có hạn mức riêng. |
| **Gemini API** | Key Google AI Studio | Dịch ngay trong tool. Có thể dùng hạn mức miễn phí nếu dự án/model/tài khoản đủ điều kiện; quota và cước do Google quyết định. Tool không thể khóa mọi lượt gọi ở mức miễn phí. |
| **OpenAI API** | Key OpenAI | Dịch ngay trong tool, phí API tính riêng với ChatGPT Free/Plus. |

Tool không tự chuyển provider, không tự thử lại hoặc dùng OpenAI trả phí khi Gemini hết quota. Bạn có thể chủ động đổi về Thủ công. Không tự điều khiển tài khoản web hoặc lấy cookie/token của ChatGPT/Gemini.

## Dùng không cần API

1. Mở **Dịch & biên tập AI**, chọn **Thủ công**.
2. Dán văn bản Trung (tối đa 8.000 ký tự), chọn Review/Tin tức/Mẹo/Giới thiệu, giọng văn, xưng hô và thời lượng.
3. Bấm **Tạo câu lệnh** rồi sao chép sang Gemini hoặc ChatGPT web. Link chỉ mở website để bạn tự thao tác.
4. AI được yêu cầu trả JSON gồm `literal`, `script`, `notes`. Sao chép đủ JSON vào ô kết quả thủ công, bấm nhập. Chấp nhận JSON được bọc trong khối markdown `json`.
5. Nếu chỉ có văn bản kịch bản, dán trực tiếp vào ô **Kịch bản tiếng Việt**; có thể điền bản dịch sát nghĩa riêng bằng tay.
6. Sửa, sao chép hoặc tải TXT UTF-8 để tạo MP3 bên ngoài. Bôi đen đoạn tối đa 600 ký tự để đưa lên khung nội dung video.

Tạo câu lệnh và nhập kết quả là xử lý cục bộ, không gọi OpenAI/Gemini API. AI web vẫn cần Internet và có giới hạn do nhà cung cấp áp dụng. Đây là quy trình thủ công, không phải bản dịch tự động chạy offline.

## Gemini API và OpenAI API

Chọn provider trong giao diện, nhập key ở **Kết nối API**. Key của từng provider giữ riêng trong bộ nhớ phiên; không lưu key trong localStorage, file hay ZIP. Tải lại trang cần nhập lại. Model được lưu riêng theo provider. Không gửi key trong chat.

- Gemini: lấy key tại https://aistudio.google.com/apikey. Model gợi ý `gemini-2.5-flash`, có thể thay bằng model tài khoản hỗ trợ. Kiểm tra điều kiện, hạn mức và giá hiện hành tại https://ai.google.dev/gemini-api/docs/pricing. Biến máy chủ: `REVIEW_GEMINI_KEY`, `GEMINI_API_KEY` hoặc `GOOGLE_API_KEY`; model mặc định tùy chọn `GEMINI_MODEL`.
- OpenAI: https://platform.openai.com/api-keys. Model mặc định `gpt-4.1-mini`, cần Responses API/Structured Outputs. Biến máy chủ: `REVIEW_OPENAI_KEY` hoặc `OPENAI_API_KEY`; model tùy chọn `OPENAI_MODEL`.

Chỉ khi bấm dịch trong chế độ API, văn bản/cấu hình gửi tới provider đã chọn. Gemini dùng HTTPS `generativelanguage.googleapis.com` với header `x-goog-api-key`, không đưa key lên URL; OpenAI dùng HTTPS `api.openai.com/v1/responses`, `store:false`. Không gửi clip/PNG tới các API dịch.

Nguồn hiện là văn bản dán vào. **Chưa có nhận lời nói từ video, OCR, lồng tiếng hay tạo MP3.** Bản dịch sát nghĩa, bản viết lại và ghi chú đều cần người dùng duyệt. Thời lượng 15/30/60/90 giây chỉ là mục tiêu; ước tính đọc 2,8 tiếng/giây. Không coi lời AI là xác minh giá, công dụng hay sự kiện.

## Dựng video

Giữ các chức năng 0.4: hệ tọa độ 720×1280 px, X/Y tính từ góc trái trên; W/H khung/video, cỡ chữ 12–144 px (nhập 90 px được), căn giữa hai trục; kéo trực tiếp bốn lớp. Video liên kết W/H 9:16 mặc định, có thể bỏ chọn để kéo giãn.

Nền một/chuyển hai màu và hòa nền alpha mềm; sáu khung dựng sẵn hoặc PNG từ máy (5 MB, 4096 px/cạnh, 8 triệu điểm ảnh; PNG động lấy hình đầu). Sáu font Sans/Serif/Mono thường/đậm kèm giấy phép. Tiêu đề/nội dung chỉnh độc lập màu/font/cỡ/vị trí/căn dòng/viền, không thêm CTA.

MP4 H.264/AAC 720×1280 giữ âm thanh gốc, nguồn tối đa 100 MB / 180 giây. Khung/video có thể nằm ngoài canvas và bị cắt; chữ vượt cạnh phải/chiều cao báo lỗi. Baseline/viền chữ giữa trình duyệt và MP4 có thể chênh nhẹ. Không xóa chữ/watermark có sẵn trên nguồn.

## Chạy và cập nhật

Cần Python 3.11+, FFmpeg/FFprobe với libx264/drawtext. Không cài pip/npm/SDK dịch vụ. Python/FFmpeg không kèm ZIP; chưa phải EXE.

```sh
python3 launch.py
```

Windows mở `START_WINDOWS.bat`; macOS/Linux chạy lệnh trong thư mục giải nén. Cổng loopback mặc định 8000; đặt `PORT` để đổi, `--no-browser` không tự mở trình duyệt. Health: `curl --fail http://127.0.0.1:8000/health`.

Dừng bản cũ, giải nén thư mục mới rồi chạy; không cần cài lại Python/FFmpeg. Thiết kế px 0.4 được giữ cùng khóa trình duyệt. Nếu cùng trình duyệt/địa chỉ/cổng và chưa có thiết kế px, có thể chuyển bản lưu 0.3 từ % sang px. PNG ở thư mục cũ cần tải lại.

## Dữ liệu và giới hạn

Thiết kế và văn bản AI lưu riêng trong localStorage; có nút xóa văn bản. Key không lưu kèm. Video/PNG/MP4 trong `.local/`, Git và gói ZIP bỏ qua. Trạng thái xuất ở RAM, mất khi dừng máy chủ: tải kết quả trước khi dừng. Chỉ xóa `.local/` khi ứng dụng đã dừng và đã giữ tệp cần thiết.

Chỉ dùng cục bộ với Host/Origin localhost; chưa có xác thực, dọn ổ đĩa, giới hạn hàng đợi video hoặc triển khai công khai. Chưa ghép nhiều clip hay đăng TikTok tự động.

## Kiểm chứng

Đã kiểm tra luồng thủ công thực qua HTTP và Chromium: không cần key, không gọi API, tạo/sao chép câu lệnh, nhập JSON thường/có code fence, từ chối JSON sai mà giữ bản cũ, xuất TXT. Gemini/OpenAI được kiểm tra bằng HTTP giả lập: định dạng request, provider/key tách biệt, hết quota không fallback/không retry, không lộ key trong URL/prompt/localStorage. Chưa gọi hai API thật vì máy kiểm tra không có key; chưa xác minh tài khoản/model cụ thể được miễn phí. Chưa chạy trực tiếp Windows/macOS.

```sh
python3 -m unittest discover -s tests -v
node --check studio.js
node --check ai_ui.js
python3 build_package.py
```

API thêm: `POST /translation-prompt` (source + phong cách → prompt, không gọi API), `POST /translation-import` (text JSON → hai bản + ghi chú), `/ai-status` trả cấu hình an toàn theo provider. `/translate` nhận thêm `provider: gemini|openai`; giá trị `manual` bị từ chối tại endpoint dịch để không vô tình gọi API.
