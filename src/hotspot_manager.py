import os
import sys
import gc

# Добавляем корневую папку проекта в sys.path для корректного импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ctypes
from threading import Thread, Event
from time import sleep
import logging
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from customtkinter import CTk, CTkLabel, CTkButton, CTkFrame, CTkEntry, CTkCheckBox, CTkTextbox, IntVar, BooleanVar, set_appearance_mode, set_default_color_theme
from pystray import Icon, Menu
from pystray import MenuItem as item

import src.api_service as api_service
import src.config_service as config_service

# Настройки
APP_NAME = "Windows Mobile Hotspot Manager"

# Запрос прав администратора
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Класс для перехвата логов в GUI
class TextboxHandler(logging.Handler):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.textbox.configure(state="normal")
            self.textbox.insert("end", msg + "\n")
            self.textbox.see("end")
            self.textbox.configure(state="disabled")
        self.textbox.after(0, append)

class HotspotManagerApp:
    def __init__(self):
        self.root = CTk()
        self.root.title(APP_NAME)
        self.root.geometry("500x550")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        self.is_running = True
        self.stop_event = Event()
        
        self.timer_minutes = IntVar(value=0)
        self.restart_minutes = IntVar(value=60) # Default to 60 for the old hourly logic
        self.autostart = BooleanVar(value=config_service.check_autostart())
        
        self.target_off_time = None
        self.last_restart_time = datetime.now()
        
        self.setup_ui()
        self.setup_logging()
        self.setup_tray()
        
        # Запуск фоновых задач
        self.bg_thread = Thread(target=self.background_worker, daemon=True)
        self.bg_thread.start()
        
        self.update_ui_state()

    def setup_ui(self):
        set_appearance_mode("System")
        set_default_color_theme("blue")

        # Индикатор статуса
        self.status_label = CTkLabel(self.root, text="Status: Unknown", font=("Arial", 18, "bold"))
        self.status_label.pack(pady=15)

        # Кнопка Вкл/Выкл
        self.toggle_btn = CTkButton(self.root, text="Turn On Hotspot", command=self.toggle_hotspot, height=40)
        self.toggle_btn.pack(pady=10)

        # Настройка таймера
        timer_frame = CTkFrame(self.root)
        timer_frame.pack(pady=10, padx=20, fill="x")
        
        CTkLabel(timer_frame, text="Shutdown Timer (minutes):").pack(side="left", padx=10)
        self.timer_entry = CTkEntry(timer_frame, textvariable=self.timer_minutes, width=60)
        self.timer_entry.pack(side="left", padx=10)
        CTkButton(timer_frame, text="Set", width=80, command=self.set_timer).pack(side="left", padx=10)

        # Настройка рестарта
        restart_frame = CTkFrame(self.root)
        restart_frame.pack(pady=10, padx=20, fill="x")
        
        CTkLabel(restart_frame, text="Auto-restart interval (minutes, 0 to disable):").pack(side="left", padx=10)
        self.restart_entry = CTkEntry(restart_frame, textvariable=self.restart_minutes, width=60)
        self.restart_entry.pack(side="left", padx=10)

        # Чекбоксы
        self.autostart_cb = CTkCheckBox(self.root, text="Start with Windows", variable=self.autostart, command=self.toggle_autostart)
        self.autostart_cb.pack(pady=10, anchor="w", padx=30)

        # Кнопка Выхода
        self.exit_btn = CTkButton(self.root, text="Exit Application", command=self.quit_app, fg_color="red", hover_color="darkred")
        self.exit_btn.pack(pady=10)
        self.log_console = CTkTextbox(self.root, height=150, state="disabled")
        self.log_console.pack(pady=5, padx=30, fill="both", expand=True)

    def setup_logging(self):
        log_format = "%(asctime)s - %(message)s"
        logging.basicConfig(filename="hotspot_manager.log", level=logging.INFO, format=log_format)
        
        gui_handler = TextboxHandler(self.log_console)
        gui_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s", "%H:%M:%S"))
        logging.getLogger().addHandler(gui_handler)
        logging.info("Application started.")

    # --- Windows API (Hotspot) ---
    def toggle_hotspot(self):
        Thread(target=self._toggle_thread, daemon=True).start()

    def _toggle_thread(self):
        self.toggle_btn.configure(state="disabled")
        is_on = api_service.get_hotspot_status()
        api_service.set_hotspot(not is_on)
        sleep(2) # Даем время системе применить статус
        self.update_ui_state()
        self.toggle_btn.configure(state="normal")

    def restart_hotspot(self):
        logging.info("Auto-restarting hotspot...")
        api_service.set_hotspot(False)
        sleep(3)
        api_service.set_hotspot(True)
        self.last_restart_time = datetime.now()
        logging.info("Auto-restart completed.")

    # --- Логика фоновых задач ---
    def set_timer(self):
        mins = self.timer_minutes.get()
        if mins > 0:
            self.target_off_time = datetime.now() + timedelta(minutes=mins)
            logging.info(f"Timer set for {mins} mins. Shutdown at {self.target_off_time.strftime('%H:%M:%S')}")
        else:
            self.target_off_time = None
            logging.info("Timer disabled.")

    def set_quick_timer(self, icon, item):
        mins = int(item.text.split()[1]) * 60 # Timer: X hours -> split gives ['Timer:', '1', 'hour']
        self.timer_minutes.set(mins)
        self.set_timer()

    def background_worker(self):
        while not self.stop_event.is_set():
            self._background_tick()
            # Ждем 5 секунд (используем event.wait для быстрой остановки)
            self.stop_event.wait(5)

    def _background_tick(self):
        is_on = api_service.get_hotspot_status()
        now = datetime.now()

        # Обработка таймера
        if self.target_off_time and is_on:
            if now >= self.target_off_time:
                logging.info("Timer triggered! Turning off hotspot.")
                api_service.set_hotspot(False)
                self.target_off_time = None
                self.timer_minutes.set(0)

        # Обработка автоперезагрузки
        restart_interval = self.restart_minutes.get()
        if restart_interval > 0 and is_on:
            if (now - self.last_restart_time).total_seconds() >= restart_interval * 60:
                self.restart_hotspot()

        # Обновление UI
        self.root.after(0, self.update_ui_state)

    def update_ui_state(self):
        is_on = api_service.get_hotspot_status()
        if is_on:
            self.status_label.configure(text="Status: On", text_color="green")
            self.toggle_btn.configure(text="Turn Off Hotspot", fg_color="red", hover_color="darkred")
            self.update_tray_icon(True)
        else:
            self.status_label.configure(text="Status: Off", text_color="gray")
            self.toggle_btn.configure(text="Turn On Hotspot", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
            self.update_tray_icon(False)

    # --- Системный трей ---
    def create_image(self, is_on):
        # Генерируем иконку (Зеленый круг - Вкл, Серый - Выкл)
        image = Image.new('RGB', (64, 64), color=(255, 255, 255))
        d = ImageDraw.Draw(image)
        color = "green" if is_on else "gray"
        d.ellipse((16, 16, 48, 48), fill=color)
        return image

    def setup_tray(self):
        # Кэшируем иконки
        self.icon_on = self.create_image(True)
        self.icon_off = self.create_image(False)

        menu = Menu(
            item('Open Settings', self.show_window, default=True),
            Menu.SEPARATOR,
            item('Timer: 1 hour', self.set_quick_timer),
            item('Timer: 2 hours', self.set_quick_timer),
            Menu.SEPARATOR,
            item('Exit', self.quit_app)
        )
        self.tray_icon = Icon("hotspot_manager", self.icon_off, APP_NAME, menu)
        
        # Запуск трея в отдельном потоке
        Thread(target=self.tray_icon.run, daemon=True).start()

    def update_tray_icon(self, is_on):
        if hasattr(self, 'tray_icon'):
            self.tray_icon.icon = self.icon_on if is_on else self.icon_off

    def hide_window(self):
        self.root.withdraw()
        gc.collect()  # Сборка мусора при сворачивании для экономии RAM

    def show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)

    # --- Автозапуск (Реестр) ---
    def toggle_autostart(self):
        config_service.set_autostart(self.autostart.get())

    def quit_app(self, icon=None, item=None):
        logging.info("Shutting down...")
        self.stop_event.set()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.quit()
        sys.exit(0)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
        
    app = HotspotManagerApp()
    app.run()
