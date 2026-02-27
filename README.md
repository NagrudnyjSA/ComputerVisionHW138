import cv2
import sys
import tkinter as tk
from threading import Thread

# Глобальные переменные
rectangles = []
running = True


def mouse_callback(event, x, y, flags, param):
    """
    Обработчик событий мыши.
    При нажатии ЛКМ добавляется прямоугольник.
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        size = 30  # Половина стороны квадрата
        rectangles.append((x - size, y - size, x + size, y + size))


def tkinter_window():
    """
    Окно tkinter с кнопкой выхода.
    """
    global running

    def quit_app():
        global running
        running = False
        root.quit()

    root = tk.Tk()
    root.title("Control Panel")

    btn = tk.Button(root, text="Quit", command=quit_app, width=20, height=2)
    btn.pack(padx=20, pady=20)

    root.mainloop()


def main():
    global running, rectangles

    if len(sys.argv) < 2:
        print("Использование: python main.py <video_source>")
        print("video_source = 0 (для вебкамеры) или путь к видеофайлу")
        return

    source = sys.argv[1]

    # Если передано число — это вебкамера
    if source.isdigit():
        source = int(source)

    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print("Ошибка открытия видеоисточника")
        return

    cv2.namedWindow("Video")
    cv2.setMouseCallback("Video", mouse_callback)

    # Запуск tkinter в отдельном потоке
    tk_thread = Thread(target=tkinter_window, daemon=True)
    tk_thread.start()

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        # Отрисовка всех сохранённых прямоугольников
        for (x1, y1, x2, y2) in rectangles:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.imshow("Video", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == ord('Q'):
            running = False
        elif key == ord('c') or key == ord('C'):
            rectangles.clear()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
