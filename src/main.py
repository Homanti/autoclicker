import sys
import threading
import time
import random
import json
import pyautogui
from pynput import mouse, keyboard

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QLineEdit, QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal


class AutoClicker:
    def __init__(self, points=None, interval=1.0, randomX=6, randomY=6):
        self.points = points if points is not None else []
        self.interval = interval
        self.running = False
        self.thread = None
        self.randomX = randomX
        self.randomY = randomY

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
                offset_x = random.randint(-self.randomX // 2, self.randomX // 2)
                offset_y = random.randint(-self.randomY // 2, self.randomY // 2)
                pyautogui.moveTo(x + offset_x, y + offset_y)
                pyautogui.click()
                time.sleep(self.interval)


class MainWindow(QMainWindow):
    new_point_signal = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Автокликер")

        self.setStyleSheet("""
            QWidget {
                background: #212121;
                color: white;
            }
            QPushButton {
                background: #303030;
                border: none;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
            QPushButton:hover {
                background: #212121;
            }
            QPushButton:pressed {
                background: #303030;
            }
            QLineEdit {
                border: none;
                background: #303030;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
            QListWidget {
                border-radius: 5px;
                border: 1px solid #303030;
            }
        """)

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

        self.deletePointButton = QPushButton("Удалить выбранную точку")
        layout.addWidget(self.deletePointButton)
        self.deletePointButton.clicked.connect(self.delete_point)

        self.intervalField = QLineEdit("1.0")
        self.randomFieldX = QLineEdit("6")
        self.randomFieldY = QLineEdit("6")
        self.intervalField.setPlaceholderText("Интервал (сек)")
        self.randomFieldX.setPlaceholderText("Смещение кликов по X (пиксели)")
        self.randomFieldY.setPlaceholderText("Смещение кликов по Y (пиксели)")
        layout.addWidget(self.intervalField)
        layout.addWidget(self.randomFieldX)
        layout.addWidget(self.randomFieldY)

        btnLayout = QHBoxLayout()
        self.startButton = QPushButton("Старт")
        self.stopButton = QPushButton("Стоп")
        btnLayout.addWidget(self.startButton)
        btnLayout.addWidget(self.stopButton)
        layout.addLayout(btnLayout)

        # Кнопки для сохранения и загрузки настроек
        settingsLayout = QHBoxLayout()
        self.saveButton = QPushButton("Сохранить настройки")
        self.loadButton = QPushButton("Загрузить настройки")
        settingsLayout.addWidget(self.saveButton)
        settingsLayout.addWidget(self.loadButton)
        layout.addLayout(settingsLayout)
        self.saveButton.clicked.connect(self.save_settings)
        self.loadButton.clicked.connect(self.load_settings)

        self.hotkeysLabel = QLabel("Горячие клавиши: Ctrl+Shift+S - Старт, Ctrl+Shift+P - Стоп")
        layout.addWidget(self.hotkeysLabel)

        self.points = []
        self.clicker = AutoClicker(points=self.points, interval=float(self.intervalField.text()),
                                   randomX=int(self.randomFieldX.text()), randomY=int(self.randomFieldY.text()))

        self.startButton.clicked.connect(self.start_clicking)
        self.stopButton.clicked.connect(self.stop_clicking)

        self.new_point_signal.connect(self.handle_new_point)

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
                return False

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
        try:
            randomX = int(self.randomFieldX.text())
        except ValueError:
            randomX = 6
        try:
            randomY = int(self.randomFieldY.text())
        except ValueError:
            randomY = 6

        self.clicker.interval = interval
        self.clicker.randomX = randomX
        self.clicker.randomY = randomY
        self.clicker.points = self.points
        self.clicker.start()

    def stop_clicking(self):
        self.clicker.stop()

    def save_settings(self):
        data = {
            "points": self.points,
            "interval": self.intervalField.text(),
            "randomX": self.randomFieldX.text(),
            "randomY": self.randomFieldY.text()
        }
        try:
            with open("settings.json", "w") as f:
                json.dump(data, f, indent=4)
            print("Настройки успешно сохранены.")
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                data = json.load(f)
            # Обновление списка точек и полей
            self.points = data.get("points", [])
            self.pointsList.clear()
            for point in self.points:
                self.pointsList.addItem(f"({point[0]}, {point[1]})")
            self.intervalField.setText(str(data.get("interval", "1.0")))
            self.randomFieldX.setText(str(data.get("randomX", "6")))
            self.randomFieldY.setText(str(data.get("randomY", "6")))
            print("Настройки успешно загружены.")
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())