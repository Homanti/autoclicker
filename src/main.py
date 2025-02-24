import sys
import threading
import time
import random
import pyautogui
from pynput import mouse, keyboard

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QLineEdit, QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal


class AutoClicker:
    def __init__(self, points=None, interval=1.0):
        self.points = points if points is not None else []
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        if not self.running and self.points:
            self.running = True
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None

    def run(self):
        while self.running:
            for (x, y) in self.points:
                if not self.running:
                    break
                # Добавляем рандомное смещение по X и Y (от -3 до 3 пикселей)
                offset_x = random.randint(-3, 3)
                offset_y = random.randint(-3, 3)
                pyautogui.moveTo(x + offset_x, y + offset_y)
                pyautogui.click()
                time.sleep(self.interval)


class MainWindow(QMainWindow):
    new_point_signal = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Автокликер")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        instructions = QLabel("Нажмите 'Выбрать точку', затем кликните ЛКМ на нужном месте экрана")
        layout.addWidget(instructions)

        self.addPointButton = QPushButton("Выбрать точку")
        layout.addWidget(self.addPointButton)
        self.addPointButton.clicked.connect(self.add_point)

        layout.addWidget(QLabel("Список точек:"))
        self.pointsList = QListWidget()
        self.pointsList.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.pointsList)

        # Кнопка для удаления выбранной точки
        self.deletePointButton = QPushButton("Удалить выбранную точку")
        layout.addWidget(self.deletePointButton)
        self.deletePointButton.clicked.connect(self.delete_point)

        self.intervalField = QLineEdit("1.0")
        self.intervalField.setPlaceholderText("Интервал (сек)")
        layout.addWidget(self.intervalField)

        btnLayout = QHBoxLayout()
        self.startButton = QPushButton("Старт")
        self.stopButton = QPushButton("Стоп")
        btnLayout.addWidget(self.startButton)
        btnLayout.addWidget(self.stopButton)
        layout.addLayout(btnLayout)

        self.hotkeysLabel = QLabel("Горячие клавиши: Ctrl+Shift+S - Старт, Ctrl+Shift+P - Стоп")
        layout.addWidget(self.hotkeysLabel)

        self.points = []
        self.clicker = AutoClicker(points=self.points, interval=float(self.intervalField.text()))

        self.startButton.clicked.connect(self.start_clicking)
        self.stopButton.clicked.connect(self.stop_clicking)

        self.new_point_signal.connect(self.handle_new_point)

        # Настройка глобальных горячих клавиш
        hotkeys = {
            '<ctrl>+<shift>+s': self.start_clicking,
            '<ctrl>+<shift>+p': self.stop_clicking
        }
        self.hotkey_listener = keyboard.GlobalHotKeys(hotkeys)
        self.hotkey_listener.start()

    def add_point(self):
        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:
                self.new_point_signal.emit((x, y))
                return False  # прекращаем прослушивание после первого клика

        listener = mouse.Listener(on_click=on_click)
        listener.start()

    def handle_new_point(self, point):
        self.points.append(point)
        self.pointsList.addItem(f"({point[0]}, {point[1]})")

    def delete_point(self):
        row = self.pointsList.currentRow()
        if row != -1:
            self.pointsList.takeItem(row)
            self.points.pop(row)

    def start_clicking(self):
        try:
            interval = float(self.intervalField.text())
        except ValueError:
            interval = 1.0
        self.clicker.interval = interval
        self.clicker.points = self.points
        self.clicker.start()

    def stop_clicking(self):
        self.clicker.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
