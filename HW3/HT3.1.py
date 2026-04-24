import cv2
import numpy as np

def order_points(pts):
    """Сортировка точек: [top-left, top-right, bottom-right, bottom-left]"""
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


# Инициализация камеры
cap = cv2.VideoCapture(0)

qr_detector = cv2.QRCodeDetector()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    original = frame.copy()

    # Поиск QR-кода
    data, points, _ = qr_detector.detectAndDecode(frame)

    if points is not None:
        points = points[0]

        # Коррекция перспективы
        warped = four_point_transform(original, points)

        # Повторное распознавание на исправленном изображении
        data_warped, _, _ = qr_detector.detectAndDecode(warped)

        # Отрисовка рамки
        pts = points.astype(int)
        cv2.polylines(frame, [pts], True, (0, 255, 0), 2)

        if data:
            print("QR (оригинал):", data)
            cv2.putText(frame, data, (pts[0][0], pts[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if data_warped:
            print("QR (исправленный):", data_warped)

        # Показываем исправленную перспективу
        cv2.imshow("Warped", warped)

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC для выхода
        break

cap.release()
cv2.destroyAllWindows()
