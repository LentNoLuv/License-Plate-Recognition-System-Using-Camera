import math
import cv2
import numpy as np
import Preprocess

ADAPTIVE_THRESH_BLOCK_SIZE = 19
ADAPTIVE_THRESH_WEIGHT = 9

n = 1
Min_char = 0.01
Max_char = 0.09

RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

# Mở camera
cap = cv2.VideoCapture(0)  # 0 là ID của camera mặc định

if not cap.isOpened():
    print("Không thể mở camera.")
    exit()

# Load mô hình KNN
npaClassifications = np.loadtxt("classifications.txt", np.float32)
npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)
npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))
kNearest = cv2.ml.KNearest_create()
kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Không thể nhận frame (kết thúc luồng?). Thoát ...")
        break

    # Giảm độ phân giải để xử lý nhanh hơn
    img = cv2.resize(frame, dsize=(400, 400))
    cv2.imshow('Camera', img)  # Hiển thị hình ảnh từ camera

    key = cv2.waitKey(1) & 0xFF  # Chờ phím nhấn
    if key == ord(' '):  # Nhấn SPACE để xử lý ảnh
        print("Đang xử lý ảnh...")
        # Tiền xử lý hình ảnh
        imgGrayscaleplate, imgThreshplate = Preprocess.preprocess(frame)
        canny_image = cv2.Canny(imgThreshplate, 250, 255)
        kernel = np.ones((3, 3), np.uint8)
        dilated_image = cv2.dilate(canny_image, kernel, iterations=1)

        # Tìm viền và lọc ra biển số xe
        contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        screenCnt = []
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.06 * peri, True)
            [x, y, w, h] = cv2.boundingRect(approx.copy())
            ratio = w / h

            # Chỉ giữ lại khung có 4 góc (giống hình chữ nhật)
            if len(approx) == 4:
                screenCnt.append(approx)
                cv2.putText(frame, str(len(approx.copy())), (x, y), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)

        # Nếu không phát hiện biển số, bỏ qua vòng lặp
        if not screenCnt:
            print("Không phát hiện biển số.")
            cv2.imshow('License Plate Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue  # Bỏ qua vòng lặp nếu không tìm thấy biển số

        # Xử lý biển số
        for cnt in screenCnt:
            cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 3)

            # Cắt vùng biển số
            mask = np.zeros(imgGrayscaleplate.shape, np.uint8)
            new_image = cv2.drawContours(mask, [cnt], 0, 255, -1)
            (x, y) = np.where(mask == 255)
            (topx, topy) = (np.min(x), np.min(y))
            (bottomx, bottomy) = (np.max(x), np.max(y))
            roi = frame[topx:bottomx, topy:bottomy]
            imgThresh = imgThreshplate[topx:bottomx, topy:bottomy]

            # Resize ảnh để xử lý OCR tốt hơn
            roi = cv2.resize(roi, (0, 0), fx=3, fy=3)
            imgThresh = cv2.resize(imgThresh, (0, 0), fx=3, fy=3)

            # Phân đoạn ký tự
            kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            thre_mor = cv2.morphologyEx(imgThresh, cv2.MORPH_DILATE, kernel3)
            cont, hier = cv2.findContours(thre_mor, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            cv2.imshow("Segmented Characters", thre_mor)
            cv2.drawContours(roi, cont, -1, (100, 255, 255), 2)

            # Nhận diện ký tự bằng KNN
            char_x = []
            char_x_ind = {}
            height, width, _ = roi.shape
            roiarea = height * width

            for ind, cnt in enumerate(cont):
                (x, y, w, h) = cv2.boundingRect(cont[ind])
                ratiochar = w / h
                char_area = w * h

                if Min_char * roiarea < char_area < Max_char * roiarea and 0.25 < ratiochar < 0.7:
                    if x in char_x:
                        x += 1
                    char_x.append(x)
                    char_x_ind[x] = ind

            # Sắp xếp các ký tự từ trái sang phải
            char_x = sorted(char_x)
            first_line, second_line = "", ""

            for i in char_x:
                (x, y, w, h) = cv2.boundingRect(cont[char_x_ind[i]])
                cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

                imgROI = thre_mor[y:y + h, x:x + w]
                imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
                npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
                npaROIResized = np.float32(npaROIResized)

                _, npaResults, _, _ = kNearest.findNearest(npaROIResized, k=3)
                strCurrentChar = str(chr(int(npaResults[0][0])))

                if y < height / 3:
                    first_line += strCurrentChar
                else:
                    second_line += strCurrentChar

            print(f"\nBiển số {n}: {first_line} - {second_line}\n")

            roi = cv2.resize(roi, None, fx=0.75, fy=0.75)
            cv2.imshow(f'Plate {n}', cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
            n += 1

        # Hiển thị hình ảnh chính
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
        cv2.imshow('License Plate Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
