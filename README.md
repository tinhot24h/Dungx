# Review Studio 0.6

Dựng video review 9:16, dịch văn bản Trung qua thủ công/Gemini/OpenAI, tạo giọng đọc qua ai33.pro.

**[Tải bản 0.6](https://github.com/tinhot24h/Dungx/raw/refs/heads/main/ReviewStudio-v0.6.zip)** · Cài/chạy: `HUONG_DAN.txt`.

## Mới: Âm thanh ai33

Mở tab **Âm thanh ai33** hoặc bấm **Tạo giọng ai33** từ kịch bản tiếng Việt:

1. Nhập **ai33.pro API key** trong ứng dụng, hoặc đặt `REVIEW_AI33_KEY` / `AI33_API_KEY` trước khi chạy máy chủ. Không dùng key Gemini/OpenAI, không gửi key trong chat.
2. Lấy kịch bản từ tab AI hoặc dán văn bản Việt. Có thể lấy nội dung review hiện tại.
3. Chọn thư viện Edge/Vbee/ElevenLabs/Minimax/Kokoro/Fish Audio/giọng clone đã có; lọc ngôn ngữ, giới tính, tìm kiếm và phân trang. Có thể nhập trực tiếp voice_id có prefix. Giọng ví dụ `edge_vi-VN-HoaiMyNeural` lấy từ tài liệu, quyền dùng giọng phụ thuộc tài khoản.
4. Chỉnh tốc độ **0,5–1,5**; có thể gửi tên file gợi ý hoặc ID từ điển phát âm đã tạo ở ai33.
5. Kiểm tra số dư credit nếu muốn, bấm **Tạo audio**. Tool gửi multipart/form-data tới API v3, giữ task_id và theo dõi qua Common API v1.
6. Khi `done`, lấy `metadata.audio_url`, tải/chuẩn hóa MP3 rồi nghe và tải trong tool. Nếu lỗi, dừng và hiển thị hướng dẫn; không tự tạo lại tác vụ.

Tạo giọng có thể trừ credit ai33, độc lập với chế độ dịch miễn API. Chi phí thực tế phụ thuộc provider/giọng/tài khoản; không tự ước tính cước. Poll mỗi 5 giây, dừng khi done/error hoặc sau 15 phút theo dõi. Dừng tự kiểm tra không hủy tác vụ ở ai33. Có thể kiểm tra task_id hoặc chọn lịch sử để lấy lại file mà không tạo lại.

MP3 tải riêng, **chưa tự thay tiếng trong video**. Nguồn TTS tối đa 1.000.000 ký tự theo tài liệu, file nguồn tải tối đa 100 MB; kịch bản rất dài nên chia đoạn. MP3 đã cache vẫn nghe/tải được khi tải lại trang; key cần nhập lại để truy vấn ai33. Khi đổi thư mục ứng dụng, file cache cũ không được chuyển tự động.

Key chỉ ở bộ nhớ phiên/server environment, không lưu file/localStorage/ZIP. Key không gửi tới CDN/media host. Link audio chỉ lấy từ tác vụ đã xác thực, không có endpoint nhận link tải tùy ý. File chuyển bằng FFmpeg có `libmp3lame`; MP3 hỗ trợ HTTP Range để tua/nghe trong trình duyệt. Định dạng nguồn hỗ trợ MP3/WAV/FLAC/Ogg/M4A, không nhận playlist.

Phạm vi hiện tại là TTS một giọng, thư viện giọng, credit và lịch sử. Chưa tạo clone mới, hội thoại nhiều người, CRUD từ điển, xóa/refund tác vụ, tải transcript hoặc ghép MP3 vào video. API contract và nguồn ảnh tài liệu: [docs/ai33-api.md](docs/ai33-api.md).

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

Nguồn hiện là văn bản dán vào. **Chưa có nhận lời nói từ video hoặc OCR. Phần dịch không tạo giọng; MP3 được tạo riêng trong tab Âm thanh ai33.** Bản dịch sát nghĩa, bản viết lại và ghi chú đều cần người dùng duyệt. Thời lượng 15/30/60/90 giây chỉ là mục tiêu; ước tính đọc 2,8 tiếng/giây. Không coi lời AI là xác minh giá, công dụng hay sự kiện.

## Dựng video

Giữ các chức năng 0.4: hệ tọa độ 720×1280 px, X/Y tính từ góc trái trên; W/H khung/video, cỡ chữ 12–144 px (nhập 90 px được), căn giữa hai trục; kéo trực tiếp bốn lớp. Video liên kết W/H 9:16 mặc định, có thể bỏ chọn để kéo giãn.

Nền một/chuyển hai màu và hòa nền alpha mềm; sáu khung dựng sẵn hoặc PNG từ máy (5 MB, 4096 px/cạnh, 8 triệu điểm ảnh; PNG động lấy hình đầu). Sáu font Sans/Serif/Mono thường/đậm kèm giấy phép. Tiêu đề/nội dung chỉnh độc lập màu/font/cỡ/vị trí/căn dòng/viền, không thêm CTA.

MP4 H.264/AAC 720×1280 giữ âm thanh gốc, nguồn tối đa 100 MB / 180 giây. Khung/video có thể nằm ngoài canvas và bị cắt; chữ vượt cạnh phải/chiều cao báo lỗi. Baseline/viền chữ giữa trình duyệt và MP4 có thể chênh nhẹ. Không xóa chữ/watermark có sẵn trên nguồn.

## Chạy và cập nhật

Cần Python 3.11+, FFmpeg/FFprobe với libx264/drawtext, libmp3lame cho MP3. Không cài pip/npm/SDK dịch vụ. Python/FFmpeg không kèm ZIP; chưa phải EXE.

```sh
python3 launch.py
```

Windows mở `START_WINDOWS.bat`; macOS/Linux chạy lệnh trong thư mục giải nén. Cổng loopback mặc định 8000; đặt `PORT` để đổi, `--no-browser` không tự mở trình duyệt. Health: `curl --fail http://127.0.0.1:8000/health`.

Dừng bản cũ, giải nén thư mục mới rồi chạy; không cần cài lại Python/FFmpeg. Thiết kế px 0.4 được giữ cùng khóa trình duyệt. Nếu cùng trình duyệt/địa chỉ/cổng và chưa có thiết kế px, có thể chuyển bản lưu 0.3 từ % sang px. PNG ở thư mục cũ cần tải lại.

## Dữ liệu và giới hạn

Thiết kế và văn bản AI lưu riêng trong localStorage; có nút xóa văn bản. Key không lưu kèm. Video/PNG/MP4/MP3 trong `.local/`, Git và gói ZIP bỏ qua. Trạng thái xuất video ở RAM, mất khi dừng máy chủ: tải kết quả trước khi dừng. Chỉ xóa `.local/` khi ứng dụng đã dừng và đã giữ tệp cần thiết.

Chỉ dùng cục bộ với Host/Origin localhost; chưa có xác thực, dọn ổ đĩa, giới hạn hàng đợi video hoặc triển khai công khai. Chưa ghép nhiều clip hay đăng TikTok tự động.

## Kiểm chứng

AI33: kiểm tra HTTP giả lập đúng API v3/v1 do người dùng cung cấp; key/header/multipart, phân trang giọng, trạng thái doing/done/error, credit/history, không retry tạo, không lộ key. FFmpeg đã chuyển WAV mẫu thành MP3 thật, FFprobe xác minh, Chromium phát/tua/download MP3 qua Range 206/416, khôi phục cache sau reload và không lưu key; bố cục 390/320px. Chưa gọi ai33 thật vì không có key và mạng môi trường chặn host; cần thử synthesis thực với tài khoản có quyền/credit.

Đã kiểm tra luồng thủ công thực qua HTTP và Chromium: không cần key, không gọi API, tạo/sao chép câu lệnh, nhập JSON thường/có code fence, từ chối JSON sai mà giữ bản cũ, xuất TXT. Gemini/OpenAI được kiểm tra bằng HTTP giả lập: định dạng request, provider/key tách biệt, hết quota không fallback/không retry, không lộ key trong URL/prompt/localStorage. Chưa gọi hai API thật vì máy kiểm tra không có key; chưa xác minh tài khoản/model cụ thể được miễn phí. Chưa chạy trực tiếp Windows/macOS.

```sh
python3 -m unittest discover -s tests -v
node --check studio.js
node --check ai_ui.js
node --check audio_ui.js
python3 build_package.py
```

API thêm: `POST /translation-prompt` (source + phong cách → prompt, không gọi API), `POST /translation-import` (text JSON → hai bản + ghi chú), `/ai-status` trả cấu hình an toàn theo provider. `/translate` nhận thêm `provider: gemini|openai`; giá trị `manual` bị từ chối tại endpoint dịch để không vô tình gọi API.

API cục bộ ai33: `GET /audio-config`, `POST /audio/voices`, `/audio/create`, `/audio/task`, `/audio/credits`, `/audio/history`, `/audio/cache`; `GET /audio/file/<asset-id>` để phát hoặc `?download=1` để tải. Không nhét API key vào query string.
