# Test Plan & Test Cases — Nhận diện biển số xe (OpenCV + KNN)

Tài liệu này mô tả kế hoạch kiểm thử và tập test case cho dự án VIETNAMESE_LICENSE_PLATE. Dùng cùng README để biết cách chạy từng script.

---

## 1. Mục tiêu kiểm thử

- Xác minh pipeline **phát hiện biển → tách ký tự → nhận dạng KNN** chạy ổn định với dữ liệu đầu vào hợp lệ.
- Phát hiện lỗi **môi trường** (thiếu file train, không mở được camera/video).
- Ghi nhận **giới hạn** (biển nghiêng, phản chiếu, độ phân giải) phù hợp với mô tả trong README.

---

## 2. Phạm vi

| Thành phần | Trong phạm vi | Ngoài phạm vi |
|------------|---------------|----------------|
| `Preprocess.py` | Tiền xử lý ảnh BGR → gray/thresh | Tối ưu tham số block size/weight |
| `GenData.py` | Sinh `classifications.txt`, `flattened_images.txt` | Đánh giá chất lượng nhãn thủ công |
| `Image_test2.py` | Ảnh tĩnh, resize 1920×1080 | So khớp 100% với ground truth tự động (chưa có harness) |
| `Video_test2.py` | Video mẫu, luồng frame | Đồng bộ âm thanh, nhiều luồng |
| `Image_test_with_camera.py` | Camera, phím SPACE/q | Nhiều camera đồng thời |

---

## 3. Môi trường & tiền điều kiện chung

| Mục | Yêu cầu |
|-----|---------|
| Python | Theo `requirements.txt` |
| OpenCV | Đọc/ghi ảnh video, camera |
| File train | `classifications.txt`, `flattened_images.txt` cùng thư mục script |
| Ảnh test | Thư mục `data/image/` (đường dẫn trong `Image_test2.py`) |
| Video test | `data/video/haihang.mp4` (hoặc đổi path trong code) |
| Video README | Khuyến nghị 1920×1080 khi quay thực tế |

**Tiêu chí Pass chung:** Không crash; với đầu vào hợp lệ, pipeline hoàn tất và có kết quả (hoặc thông báo “không phát hiện” rõ ràng).

---

## 4. Phân loại kiểm thử

| Loại | Mô tả ngắn |
|------|------------|
| Chức năng (functional) | Đúng luồng: preprocess → contour → (xoay) → segment → KNN |
| Âm (negative) | File thiếu, ảnh hỏng, camera không mở được |
| Khả năng sử dụng (usability) | Phím tắt, cửa sổ hiển thị |
| Hiệu năng nhẹ (smoke) | Thời gian phản hồi frame trên máy mục tiêu |
| Cài đặt & cấu hình | Cài dependency, đặt đúng đường dẫn ảnh/video trong code |
| Tương thích (compatibility) | Windows/Linux, phiên bản Python/OpenCV khác nhau |
| Hồi quy (regression) | Lặp lại bộ smoke + TC liên quan module vừa sửa |
| **Functional Testing** | Kiểm tra từng **chức năng / module** đúng đặc tả (tiền xử lý, phát hiện biển, tách ký tự, KNN, GenData…) — mục **6.6**. |
| **System Testing** | Kiểm tra **toàn hệ thống** đầu cuối: cài đặt, luồng ảnh/video/camera, tương tác người dùng, phụ thuộc tệp — mục **6.7**. |

**Functional vs System (tóm tắt):** Functional tập trung “**đúng từng bước**” và có thể lần theo một script/module; System tập trung “**đúng cả luồng người dùng + môi trường**”, gần kịch bản vận hành thật.

---

## 4.1 Giả định, ràng buộc, phụ thuộc

| Loại | Nội dung |
|------|----------|
| Giả định | Người kiểm thử có quyền đọc/ghi thư mục dự án; webcam/video là tùy chọn theo nhóm TC. |
| Ràng buộc | Độ chính xác nhận dạng phụ thuộc tập train và thuật toán KNN; không cam kết % chính xác mà README chưa nêu cho môi trường cụ thể. |
| Phụ thuộc | Thư viện trong `requirements.txt`; file `classifications.txt` và `flattened_images.txt` đồng bộ (cùng số mẫu). |

---

## 4.2 Chiến lược kiểm thử & ưu tiên theo rủi ro

**Thứ tự gợi ý:** (1) Smoke end-to-end một ảnh + có/không file train → (2) Âm (thiếu file, sai path) → (3) Video ngắn → (4) Camera → (5) Bộ ảnh đa dạng (góc, ánh sáng) nếu có.

**Rủi ro cao (ưu tiên kiểm tra nhiều hơn):**

| Rủi ro | Tác động | Hành động kiểm thử |
|--------|----------|---------------------|
| Thiếu / hỏng file KNN | Crash ngay khi chạy | TC-DATA-02, kiểm tra thông báo lỗi |
| Sai đường dẫn ảnh/video | Không có kết quả, khó phân biệt lỗi code | Chuẩn hóa checklist mục 16 |
| Phản chiếu, biển nghiêng | Sai vùng biển hoặc sai ký tự | Ảnh mẫu riêng trong test data; ghi limitation |
| Thay đổi tham số OpenCV | Hồi quy phát hiện contour | Regression sau mỗi chỉnh `approxPolyDP`, Canny, ngưỡng |

---

## 5. Ma trận traceability (module → nhóm TC)

| Module / Script | ID test case |
|-----------------|--------------|
| `Preprocess.preprocess` | TC-PRE-01 … TC-PRE-03 |
| Dữ liệu KNN / `GenData` | TC-DATA-01 … TC-DATA-03 |
| `Image_test2.py` | TC-IMG-01 … TC-IMG-05 |
| `Video_test2.py` | TC-VID-01 … TC-VID-04 |
| `Image_test_with_camera.py` | TC-CAM-01 … TC-CAM-04 |
| Functional (theo tính năng) | TC-FUNC-01 … TC-FUNC-10 |
| System (E2E + vận hành) | TC-SYS-01 … TC-SYS-07 |

### 5.1 Ánh xạ yêu cầu (README) → kiểm chứng

| Nội dung README / yêu cầu ngầm | Cách kiểm chứng |
|--------------------------------|-----------------|
| Phát hiện biển (contour, tỷ lệ…) | TC-IMG-*, TC-VID-* (quan sát viền xanh / log) |
| Tách & nhận dạng ký tự (KNN, 20×30) | TC-DATA-01, TC-IMG-02/03 |
| Chạy từ ảnh / video / camera | TC-IMG-01, TC-VID-01, TC-CAM-01 |
| Video khuyến nghị 1920×1080 | TC-IMG-05, ghi nhận khi dùng độ phân giải khác |
| Luồng hoàn chỉnh theo kênh đầu vào | TC-SYS-01 … TC-SYS-03 |
| Cài đặt & vận hành như người dùng cuối | TC-SYS-04 … TC-SYS-07 |

### 5.2 Functional → component gốc (tham chiếu nhanh)

| ID Functional | Chức năng đang kiểm tra | Liên quan script / module |
|---------------|-------------------------|---------------------------|
| TC-FUNC-01 … 02 | Tiền xử lý ảnh | `Preprocess.py` |
| TC-FUNC-03 … 04 | Phát hiện vùng biển (contour, lọc 4 cạnh) | `Image_test2.py`, `Video_test2.py`, `Image_test_with_camera.py` |
| TC-FUNC-05 … 06 | Xoay / cắt ROI biển (nếu có trong luồng) | `Image_test2.py`, `Video_test2.py` |
| TC-FUNC-07 … 08 | Tách ký tự, thứ tự trái → phải, hai dòng | Cùng các script recognition |
| TC-FUNC-09 | Huấn luyện / sinh dữ liệu KNN | `GenData.py` + file `.txt` |
| TC-FUNC-10 | KNN: ảnh chữ 20×30 → lớp ASCII | `cv2.ml.KNearest` trong các script test |

### 5.3 System → phạm vi tổng thể

| ID System | Phạm vi |
|-----------|---------|
| TC-SYS-01 … 03 | E2E: ảnh tĩnh / video / camera |
| TC-SYS-04 … 05 | Cài đặt, cấu hình đường dẫn, phụ thuộc tệp |
| TC-SYS-06 … 07 | Ổn định khi dùng (thoát, tài nguyên), tái chạy |

---

## 6. Test cases — chi tiết

### 6.1 Tiền xử lý (`Preprocess.py`)

| ID | Mô tả | Tiền điều kiện | Các bước | Kết quả mong đợi |
|----|--------|----------------|----------|------------------|
| TC-PRE-01 | Ảnh BGR hợp lệ | `cv2.imread` đọc được file JPG/PNG | Gọi `Preprocess.preprocess(img)` | Trả về tuple 2 phần tử: grayscale `uint8`, binary `uint8`; kích thước trùng chiều cao/rộng ảnh gốc |
| TC-PRE-02 | Ảnh có biển tương phản tốt | Ảnh bãi xe, biển rõ | Gọi preprocess, soi `imgThresh` (debug) | Vùng biển/nền phân tách được ở mức nhị phân (subjective: không toàn đen/trắng vô nghĩa) |
| TC-PRE-03 | Ảnh rất nhỏ | Ảnh 64×64 | Gọi preprocess | Không exception; output shape = input shape |

### 6.2 Dữ liệu huấn luyện KNN

| ID | Mô tả | Tiền điều kiện | Các bước | Kết quả mong đợi |
|----|--------|----------------|----------|------------------|
| TC-DATA-01 | File train đầy đủ | `classifications.txt`, `flattened_images.txt` tồn tại | `np.loadtxt`; `flattened_images` có `N` hàng, mỗi hàng 600 cột (20×30); `classifications` có `N` phần tử | `kNearest.train(...)` không báo lỗi kích thước |
| TC-DATA-02 | Thiếu file | Đổi tên tạm `classifications.txt` | Chạy `Image_test2.py` | Exception / lỗi đọc file rõ ràng (hoặc thoát an toàn nếu đã bọc try) |
| TC-DATA-03 | `GenData.py` với `training_chars.png` | File PNG có trong project | Chạy `GenData.py`, nhập nhãn hợp lệ cho vài ký tự | Sinh/ghi được file `.txt`; contour area > `MIN_CONTOUR_AREA` mới hỏi nhãn |

### 6.3 Ảnh tĩnh (`Image_test2.py`)

| ID | Mô tả | Tiền điều kiện | Các bước | Kết quả mong đợi |
|----|--------|----------------|----------|------------------|
| TC-IMG-01 | Đường dẫn ảnh đúng | Sửa `cv2.imread` trỏ tới file có trong `data/image/` | Chạy script | Script chạy hết; có cửa sổ hoặc log kết quả chuỗi biển (có thể sai từng ký tự nhưng pipeline chạy) |
| TC-IMG-02 | Biển 1 hàng | Ảnh có biển một dòng | Chạy | `first_line` hoặc `second_line` phản ánh tách dòng theo `y < height/3` |
| TC-IMG-03 | Biển 2 hàng | Ảnh hai dòng số/chữ | Chạy | Hai phần chuỗi (line1 - line2) khớp trực quan ít nhất số lượng ký tự gần đúng |
| TC-IMG-04 | Không có biển trong ảnh | Ảnh nền xe/không contour 4 cạnh | Chạy | Thông báo kiểu “No plate detected” hoặc không vào nhánh vẽ biển |
| TC-IMG-05 | Độ phân giải khác 1920×1080 | Comment dòng resize hoặc đổi kích thước | Chạy | Vẫn chạy; tỷ lệ phát hiện có thể thay đổi (ghi defect nếu fail thường xuyên) |

### 6.4 Video (`Video_test2.py`)

| ID | Mô tả | Tiền điều kiện | Các bước | Kết quả mong đợi |
|----|--------|----------------|----------|------------------|
| TC-VID-01 | Video mẫu tồn tại | `data/video/haihang.mp4` | Chạy, quan sát vài giây | `cap.isOpened()` true; frame đọc được; cửa sổ hiển thị |
| TC-VID-02 | Thống kê frame | Cùng trên | Ghi lại console `total frame`, `number of plates found` | Giá trị tăng/giảm hợp lý, không NaN |
| TC-VID-03 | Thoát an toàn | Đang chạy | Nhấn `q` | Vòng lặp dừng; `cap.release()`; không treo cửa sổ vĩnh viễn |
| TC-VID-04 | Sai đường dẫn video | Đổi `VideoCapture` sang file không tồn tại | Chạy | Không crash vô hạn; `read()` false hoặc hành vi OpenCV document |

### 6.5 Camera trực tiếp (`Image_test_with_camera.py`)

| ID | Mô tả | Tiền điều kiện | Các bước | Kết quả mong đợi |
|----|--------|----------------|----------|------------------|
| TC-CAM-01 | Mở camera mặc định | Webcam driver OK | Chạy script | `cap.isOpened()` true; cửa sổ “Camera” hiển thị luồng |
| TC-CAM-02 | Không có camera | Tắt webcam / chọn máy ảo | Chạy | In “Không thể mở camera.” và thoát |
| TC-CAM-03 | Chụp / xử lý frame | Biển trong khung, nhấn SPACE | SPACE | Log “Đang xử lý ảnh…”; nếu có biển: cửa sổ detection/segment; nếu không: “Không phát hiện biển số.” |
| TC-CAM-04 | Thoát | Đang chạy | Nhấn `q` | Giải phóng `cap`, đóng window |

### 6.6 Functional Testing — test case theo chức năng

*Mục tiêu:* xác nhận **từng khối chức năng** hoạt động đúng với đầu vào đại diện; có thể tái sử dụng cùng dữ liệu với mục 6.1–6.5 nhưng **nhóm theo “tính năng”** để báo cáo / traceability.

| ID | Chức năng | Tiền điều kiện | Các bước | Kết quả mong đợi |
|----|------------|----------------|----------|------------------|
| TC-FUNC-01 | **F_preprocess:** xuất grayscale + binary | Ảnh BGR hợp lệ | `Preprocess.preprocess(img)` | Hai ma trận cùng kích thước ảnh; `imgThresh` dạng nhị phân (0/255) |
| TC-FUNC-02 | **F_preprocess:** bảo toàn chiều sau `extractValue` | Ảnh 720×1280×3 | Gọi preprocess | `shape[:2]` của output trùng 720×1280 |
| TC-FUNC-03 | **F_detect:** lọc contour gần tứ giác | Ảnh có biển rõ | Chạy pipeline đến bước `approxPolyDP`, đếm `len(approx)==4` trong top contours | Ít nhất một candidate thỏa 4 đỉnh khi biển hiển thị rõ |
| TC-FUNC-04 | **F_detect:** không báo “có biển” khi không đủ 4 cạnh | Ảnh không có biển hoặc nhiễu | Chạy `Image_test2.py` | `screenCnt` rỗng hoặc nhánh “No plate detected” |
| TC-FUNC-05 | **F_geometric:** crop ROI theo mask contour | Đã có `screenCnt` hợp lệ | Theo code: mask → `np.where` → crop `roi` | `roi` không rỗng (chiều > 0) khi contour hợp lệ |
| TC-FUNC-06 | **F_geometric:** xoay biển (luồng có xoay) | `Video_test2.py` / `Image_test2.py` có phép xoay | Chạy với ảnh biển nghiêng nhẹ | Ảnh sau `warpAffine` thẳng hơn trực quan; không crash |
| TC-FUNC-07 | **F_segment:** tách contour ký tự sau morp | `thre_mor` có chữ tách được | `findContours` + lọc diện tích/tỉ lệ | Số bbox ký tự trong khoảng hợp lý (vd 7–9 với biển đầy đủ — theo logic script) |
| TC-FUNC-08 | **F_order:** gán ký tự dòng 1 vs dòng 2 | Biển 2 hàng | Quan sát điều kiện `y < height/3` | Ký tự trên cùng vào `first_line`, dưới vào `second_line` |
| TC-FUNC-09 | **F_traindata:** GenData ghi cặp nhãn–vector | `training_chars.png` tồn tại | Chạy `GenData.py`, nhập vài nhãn | File `.txt` cập nhật; số dòng `flattened` khớp số nhãn đã thêm (trong phiên làm việc) |
| TC-FUNC-10 | **F_knn:** truy vấn một patch chữ | KNN đã `train`; patch đã resize 20×30 | `findNearest(..., k=3)` | Trả về mã ASCII hợp lệ (ký tự trong bộ `0-9A-Z` của bộ train) |

---

### 6.7 System Testing — kiểm thử hệ thống (end-to-end)

*Mục tiêu:* kiểm tra **toàn bộ ứng dụng** như người dùng / vận hành: cài đặt, tệp kèm theo, luồng ảnh hoặc video hoặc camera, tương tác thoát; không giả định tester can thiệp code từng dòng.

| ID | Kịch bản hệ thống | Tiền điều kiện | Các bước | Kết quả mong đợi |
|----|-------------------|----------------|----------|------------------|
| TC-SYS-01 | **E2E ảnh tĩnh:** từ mở tool đến xem kết quả | Môi trường E1–E4; ảnh đúng path trong `Image_test2.py` | Mở terminal tại thư mục gốc → `python Image_test2.py` | Không crash; cửa sổ/stdout hiển thị kết quả; có thể đóng cửa sổ bình thường |
| TC-SYS-02 | **E2E video:** đọc file, xử lý liên tục, dừng | `haihang.mp4` (hoặc path tương đương) tồn tại | `python Video_test2.py`; quan sát > 10 s; `q` | Luồng hiển thị; log/thống kê chạy; thoát sạch (không phải kill -9) |
| TC-SYS-03 | **E2E camera:** xem trước → SPACE xử lý → thoát | Webcam hoạt động | `python Image_test_with_camera.py`; SPACE khi có cảnh; `q` | Luồng camera mượt; sau SPACE có phản hồi xử lý hoặc thông báo không phát hiện; giải phóng camera |
| TC-SYS-04 | **Cài đặt hệ thống:** dependency đầy đủ | Python sạch hoặc venv mới | `pip install -r requirements.txt` | Cài đặt thành công; import `cv2`, `numpy` không lỗi |
| TC-SYS-05 | **Phụ thuộc dữ liệu:** hệ thống không chạy E2E nếu thiếu train | Xóa/đổi tên tạm một file `.txt` train | Chạy `Image_test2.py` | Lỗi rõ ràng hoặc hành vi đã tài liệu hóa; không treo im lặng vô hạn |
| TC-SYS-06 | **Ổn định:** chạy lặp E2E ảnh 3 lần liên tiếp | Không đổi dữ liệu | Chạy `Image_test2.py` × 3 | Mỗi lần kết thúc bình thường; không rò rỉ cửa sổ/process treo (quan sát Task Manager tùy chọn) |
| TC-SYS-07 | **Tương thích môi trường:** cùng bước E2E trên máy khác hoặc OS khác *(nếu trong phạm vi)* | Ghi rõ OS/Python/OpenCV trong báo cáo | TC-SYS-01 hoặc TC-SYS-02 | Hành vi tương đương môi trường chuẩn; chênh lệch ghi vào ma trận mục 12 |

**Gợi ý bộ smoke System:** TC-SYS-01 + TC-SYS-04 (và TC-SYS-05 nếu cần chứng minh xử lý lỗi tệp).

---

## 7. Quản lý khiếm khuyết (bug / limitation)

Khi FAIL, ghi:

- **ID** test case, phiên bản code, OS, OpenCV version  
- **Ảnh/video mẫu** (đính kèm hoặc hash file)  
- **Kỳ vọng vs thực tế** (chuỗi nhận dạng, có/không contour)  
- **Mức độ**: Blocker / Major / Minor / UX  

Các nhóm lỗi thường gặp (theo README): phản chiếu ô tô, biển nghiêng nhiều, nhầm ký tự (1/7, 0/6, B/8…).

---

## 8. Tiêu chí kết thúc kiểm thử (Exit criteria) — gợi ý

- Tất cả TC **smoke** (TC-PRE-01, TC-DATA-01, TC-IMG-01, TC-VID-01, TC-CAM-01) Pass trên môi trường chuẩn.  
- **Functional smoke:** TC-FUNC-01, TC-FUNC-03, TC-FUNC-10 Pass (hoặc tương đương với tập train hiện có).  
- **System smoke:** TC-SYS-01, TC-SYS-04 Pass.  
- Không còn crash khi thiếu file train (hoặc đã có xử lý + tài liệu hướng dẫn).  
- Các TC âm (thiếu file, không camera) có hành vi **dự kiến** đã ghi trong bảng.  
- **Blocker** đã xử lý hoặc được chấp nhận tạm (kèm kế hoạch); không để lỗi crash không ghi nhận.

---

## 8.1 Tiêu chí bắt đầu kiểm thử (Entry criteria)

| # | Điều kiện |
|---|-----------|
| E1 | Build/script có thể chạy từ thư mục gốc sau khi cài `requirements.txt`. |
| E2 | `classifications.txt` và `flattened_images.txt` hiện diện (trừ khi chủ đích chạy TC âm). |
| E3 | Ít nhất một ảnh trong `data/image/` (hoặc path trong `Image_test2.py` trỏ tới file tồn tại). |
| E4 | Phiên bản Python/OpenCV đã ghi trong báo cáo tổng hợp (mục 15). |

---

## 9. Lịch & trách nhiệm (mẫu)

| Giai đoạn | Nội dung |
|-----------|----------|
| Chuẩn bị | Cài `requirements.txt`, kiểm tra file train và `data/` |
| Smoke | 1 ngày — chạy TC-PRE, TC-DATA-01, TC-IMG-01, TC-VID-01, TC-CAM-01 |
| Regression | Sau mỗi thay đổi Preprocess / ngưỡng contour / KNN |

**Gợi ý vai trò:** Người thực hiện (tester), người xem xét kết quả (lead/PM), người sửa lỗi (dev) — có thể trùng nhau trong dự án nhỏ.

---

## 10. Sản phẩm bàn giao kiểm thử (Test deliverables)

| STT | Tài liệu / nội dung |
|-----|---------------------|
| 1 | `TEST_PLAN.md` (kế hoạch + test case) |
| 2 | Báo cáo lỗi (mục 17) cho mỗi defect |
| 3 | Báo cáo tổng hợp vòng kiểm thử (mục 15) |
| 4 | Bộ ảnh/video mẫu + mô tả (thư mục / tên file) dùng để tái hiện |
| 5 | (Tùy chọn) Kết quả đo thời gian xử lý frame / clip ngắn |

---

## 11. Đặc tả dữ liệu thử (Test data)

| Nhóm | Mô tả | Ghi chú |
|------|--------|---------|
| Ảnh “vàng” | Biển 1 hàng, sáng, thẳng | Baseline so sánh sau chỉnh code |
| Ảnh “khó” | Phản chiếu, bóng, nghiêng >10°, bẩn | Kỳ vọng: phần lớn ghi limitation, không bắt buộc Pass |
| Ảnh âm | Không có biển, chỉ nền | TC-IMG-04 |
| Video | Ngắn (vài chục giây) + đúng codec OpenCV đọc được | Tránh file quá nặng khi smoke |
| Train | Bản sao lưu `classifications.txt` / `flattened_images.txt` trước khi chạy `GenData.py` | Tránh mất dữ liệu cũ |

**Quản lý phiên bản:** Nên đặt tên file theo quy ước (`plate_01_frontal.jpg`) và ghi trong báo cáo hash hoặc ngày chụp nếu cần truy vết.

---

## 12. Ma trận tương thích (Compatibility matrix) — mẫu

| OS | Python | OpenCV | Camera | Ảnh | Video | Ghi chú / Ngày |
|----|--------|--------|--------|-----|-------|----------------|
| Windows 10/11 | … | … | Pass/Fail | Pass/Fail | Pass/Fail | |
| (tùy chọn) Ubuntu … | … | … | … | … | … | |

Điền sau mỗi đợt kiểm thử; không bắt buộc đủ mọi ô nếu phạm vi chỉ một OS.

---

## 13. Tạm dừng & tiếp tục kiểm thử (Suspension / resumption)

| Tạm dừng khi | Tiếp tục khi |
|--------------|----------------|
| Crash liên tục không có workaround | Đã có bản vá / commit mới được xác nhận |
| Thiếu dữ liệu (video/ảnh) không thể thay | File bổ sung đã đặt đúng path |
| Môi trường máy (driver camera) hỏng | Thiết bị hoặc máy thay thế sẵn sàng |

---

## 14. Mẫu báo cáo lỗi (Defect report)

Sao chép bảng sau và điền cho mỗi lỗi:

| Trường | Nội dung |
|--------|----------|
| **ID lỗi** | DEF-001 … |
| **Tiêu đề** | Ngắn gọn (vd: Crash khi thiếu classifications.txt) |
| **Môi trường** | OS, Python `x.y`, OpenCV `x.y.z`, commit/hash git (nếu có) |
| **Test case liên quan** | VD: TC-DATA-02 |
| **Mức độ** | Blocker / Major / Minor / Suggestion |
| **Các bước tái hiện** | 1. … 2. … |
| **Kết quả mong đợi** | … |
| **Kết quả thực tế** | … |
| **Dữ liệu kèm theo** | Tên file ảnh/video, ảnh chụp màn hình |
| **Ghi chú** | Workaround (nếu có) |

---

## 15. Mẫu báo cáo kết quả kiểm thử (Test summary report)

| Trường | Nội dung |
|--------|----------|
| **Phiên bản phần mềm** | Commit / tag / mô tả ngày build |
| **Ngày / người thực hiện** | |
| **Phạm vi** | Smoke / Full manual / Regression (mô tả) |
| **Môi trường** | Như mục 12 |
| **Tổng số TC chạy** | Pass: … Fail: … Blocked: … N/A: … |
| **Tóm tắt lỗi** | Số Blocker/Major/Minor; liệt kê ID DEF-… |
| **Kết luận** | Sẵn sàng dùng thử / Chấp nhận có điều kiện / Không đạt |
| **Rủi ro còn lại** | VD: nhầm 1/7 dưới ánh sáng yếu |

---

## 16. Checklist nhanh (trước bàn giao / smoke hàng ngày)

- [ ] `pip install -r requirements.txt` (hoặc môi trường ảo tương đương) thành công  
- [ ] Hai file `.txt` train nằm cùng thư mục với script test  
- [ ] `Image_test2.py`: `cv2.imread` trỏ file tồn tại  
- [ ] `Video_test2.py`: đường dẫn video đúng (nếu chạy video)  
- [ ] Chạy smoke: TC-PRE-01 (hoặc import + gọi preprocess), TC-IMG-01, TC-DATA-01  
- [ ] Functional smoke: TC-FUNC-01, TC-FUNC-03, TC-FUNC-10  
- [ ] System smoke: TC-SYS-04 (cài đặt), TC-SYS-01 (`Image_test2.py` E2E)  
- [ ] Ghi Python/OpenCV version nếu phát hiện lỗi lạ để tái hiện  

---

## 17. Ghi chú bảo mật & quyền riêng tư (nhẹ)

Ứng dụng dùng camera: không lưu video/ảnh biển thật vào kho công cộng khi kiểm thử thực địa nếu chính sách nội bộ không cho phép; dùng ảnh tổng hợp hoặc biển mờ trong báo cáo defect.

---

## 18. Thuật ngữ

| Thuật ngữ | Giải thích ngắn |
|-----------|------------------|
| Smoke test | Kiểm tra nhanh “có chạy được không” trên luồng chính |
| Regression | Kiểm thử lại sau khi sửa code để đảm bảo không phá tính năng cũ |
| Ground truth | Biển số đúng do người gán, để đo độ chính xác (dự án chưa bắt buộc) |
| Limitation | Giới hạn thuật toán/ngữ cảnh, không phải lỗi cài đặt |
| Functional Testing | Kiểm thử theo **chức năng / module** (tiền xử lý, phát hiện biển, KNN…) |
| System Testing | Kiểm thử **cả hệ** end-to-end: cài đặt, luồng người dùng, tệp và thiết bị |
| E2E (end-to-end) | Luồng đầy đủ từ đầu vào người dùng đến đầu ra hiển thị / log |

---

*Tài liệu bổ sung cho README; cập nhật khi thêm automated test (pytest) hoặc bộ ảnh chuẩn ground truth.*
