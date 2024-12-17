import flet as ft
import pyautogui
import threading
import time

from pynput import mouse, keyboard

class AutoClicker:
    def __init__(self, points=None, interval=1.0):
        self.points = points if points else []
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        if not self.running and self.points:
            self.running = True
            self.thread = threading.Thread(target=self.run)
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
                pyautogui.moveTo(x, y)
                pyautogui.click()
                time.sleep(self.interval)

def main(page: ft.Page):
    page.title = "Автокликер"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    interval_field = ft.TextField(label="Интервал (сек)", value="1.0", width=100)
    points_list = ft.Column()
    points = []
    clicker = AutoClicker(points=points, interval=float(interval_field.value))

    def on_click(x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            points.append((x, y))
            points_list.controls.append(ft.Text(f"({x}, {y})"))
            page.update()
            return False

    def add_point_from_mouse(e):
        listener = mouse.Listener(on_click=on_click)
        listener.start()

    def start_clicking(e):
        try:
            clicker.interval = float(interval_field.value)
        except ValueError:
            clicker.interval = 1.0
        clicker.points = points
        clicker.start()

    def stop_clicking(e):
        clicker.stop()

    add_btn = ft.ElevatedButton(text="Выбрать точку", on_click=add_point_from_mouse)
    start_btn = ft.ElevatedButton(text="Старт", on_click=start_clicking)
    stop_btn = ft.ElevatedButton(text="Стоп", on_click=stop_clicking)

    page.add(
        ft.Text("Нажмите 'Выбрать точку', затем кликните ЛКМ на нужном месте экрана"),
        add_btn,
        ft.Text("Список точек:"),
        points_list,
        interval_field,
        ft.Row([start_btn, stop_btn], alignment=ft.MainAxisAlignment.CENTER),
        ft.Text("Горячие клавиши: Ctrl+Shift+S - Старт, Ctrl+Shift+P - Стоп")
    )

    # Функции для хоткеев
    def on_hotkey_start():
        start_clicking(None)

    def on_hotkey_stop():
        stop_clicking(None)

    hotkeys = {
        '<ctrl>+<shift>+s': on_hotkey_start,
        '<ctrl>+<shift>+p': on_hotkey_stop
    }

    listener = keyboard.GlobalHotKeys(hotkeys)
    listener.start()

ft.app(target=main)