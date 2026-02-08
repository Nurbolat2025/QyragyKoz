import customtkinter as ctk
import os
import shutil
import time
import datetime
import threading
import sys
import hashlib
import requests
import json
import re
import winreg
from PIL import Image
import pystray
from pystray import MenuItem as item
import win32api
import win32file
import win32con
import wmi
import pythoncom

# --- БАПТАУЛАР / SETTINGS ---
TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"  
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"  
VIRUSTOTAL_API_KEY = "YOUR_API_KEY_HERE" 

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """ Ресурстарға жолды анықтау (EXE ішінде иконка табылуы үшін) """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Жұмыс папкалары мен файлдары
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUARANTINE_FOLDER = os.path.join(BASE_DIR, "QyragyKoz_Quarantine")
ALLOW_LIST_FILE = os.path.join(BASE_DIR, "allowed_keyboards.json")
ICON_PATH = resource_path("QyragyKoz.ico")
DANGEROUS_EXTENSIONS = ['.lnk', '.vbs', '.bat', '.cmd', '.scr', '.pif', '.wsf', '.js', '.jse']

# --- АУДАРМАЛАР (TRANSLATIONS) ---
TRANSLATIONS = {
    "KZ": {
        "title": "QYRAGY KOZ\n🛡️ GLOBAL", "scan": "ТОЛЫҚ ТЕКСЕРУ", "vaccine": "💉 Вакцинация жасау",
        "quarantine": "Карантинді ашу", "kill": "Вирус процесті жою", "status": "Жүйе күту режимінде...",
        "lang": "Тіл / Language:", "paranoid": "Paranoid Mode", "msg_done": "Аяқталды!"
    },
    "EN": {
        "title": "QYRAGY KOZ\n🛡️ GLOBAL", "scan": "FULL SCAN", "vaccine": "💉 Vaccinate USB",
        "quarantine": "Open Quarantine", "kill": "Kill Virus Processes", "status": "System is idle...",
        "lang": "Language:", "paranoid": "Paranoid Mode", "msg_done": "Finished!"
    },
    "RU": {
        "title": "QYRAGY KOZ\n🛡️ GLOBAL", "scan": "ПОЛНОЕ СКАНИРОВАНИЕ", "vaccine": "💉 Вакцинация USB",
        "quarantine": "Открыть карантин", "kill": "Убить процессы", "status": "Ожидание...",
        "lang": "Язык:", "paranoid": "Paranoid Mode", "msg_done": "Готово!"
    }
}

class QyragyKozApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QYRAGY KOZ GLOBAL 4.0")
        self.geometry("850x650")
        self.resizable(False, False)
        
        # 1. Интерфейсті құру (Бірінші кезекте!)
        self.current_lang = "KZ"
        self.setup_ui() 
        
        # 2. Жүйелік функциялар
        self.add_to_startup()
        self.withdraw() # Трейде жасырын бастау
        self.protocol('WM_DELETE_WINDOW', self.hide_window)
        
        if not os.path.exists(QUARANTINE_FOLDER):
            os.makedirs(QUARANTINE_FOLDER)
            
        self.allowed_keyboards = self.load_allowlist()
        self.monitoring = True
        
        # 3. Фондық ағындар
        threading.Thread(target=self.setup_tray, daemon=True).start()
        threading.Thread(target=self.usb_monitor_loop, daemon=True).start()
        threading.Thread(target=self.hid_monitor_loop, daemon=True).start()

        # 4. Бағдарлама іске қосылғанын хабарлау
        self.after(2000, self.start_notification)

    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text=TRANSLATIONS[self.current_lang]["title"], font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=20)
        
        self.lang_menu = ctk.CTkOptionMenu(self.sidebar, values=["KZ", "EN", "RU"], command=self.change_language)
        self.lang_menu.pack(padx=20, pady=5)
        
        self.btn_scan_all = ctk.CTkButton(self.sidebar, text=TRANSLATIONS[self.current_lang]["scan"], fg_color="green", command=self.start_scan_all)
        self.btn_scan_all.pack(padx=20, pady=10)
        
        self.btn_vaccine = ctk.CTkButton(self.sidebar, text=TRANSLATIONS[self.current_lang]["vaccine"], fg_color="#D35400", command=self.start_vaccine)
        self.btn_vaccine.pack(padx=20, pady=10)
        
        self.btn_kill = ctk.CTkButton(self.sidebar, text=TRANSLATIONS[self.current_lang]["kill"], fg_color="red", command=self.kill_virus_processes)
        self.btn_kill.pack(padx=20, pady=10)

        self.btn_quarantine = ctk.CTkButton(self.sidebar, text=TRANSLATIONS[self.current_lang]["quarantine"], command=lambda: os.startfile(QUARANTINE_FOLDER))
        self.btn_quarantine.pack(padx=20, pady=10)
        
        self.paranoid_var = ctk.BooleanVar(value=False)
        self.switch_paranoid = ctk.CTkSwitch(self.sidebar, text=TRANSLATIONS[self.current_lang]["paranoid"], variable=self.paranoid_var)
        self.switch_paranoid.pack(padx=20, pady=20)

        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.lbl_status = ctk.CTkLabel(self.main_frame, text=TRANSLATIONS[self.current_lang]["status"])
        self.lbl_status.pack(pady=10)
        
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.set(0)
        
        self.log_box = ctk.CTkTextbox(self.main_frame, width=400, height=300)
        self.log_box.pack(padx=10, pady=10, fill="both", expand=True)

    def change_language(self, new_lang):
        """ Тіл ауыстыру және барлық мәтіндерді жаңарту """
        self.current_lang = new_lang
        t = TRANSLATIONS[new_lang]
        self.logo_label.configure(text=t["title"])
        self.btn_scan_all.configure(text=t["scan"])
        self.btn_vaccine.configure(text=t["vaccine"])
        self.btn_kill.configure(text=t["kill"])
        self.btn_quarantine.configure(text=t["quarantine"])
        self.switch_paranoid.configure(text=t["paranoid"])
        self.lbl_status.configure(text=t["status"])
        self.log(f"Language changed to {new_lang}")

    def add_to_startup(self):
        """ Windows автозагрузкасына қосу """
        path = sys.executable if getattr(sys, 'frozen', False) else os.path.realpath(sys.argv[0])
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "QyragyKoz", 0, winreg.REG_SZ, path)
            winreg.CloseKey(key)
            self.log("✅ Автозагрузкаға қосылды.")
        except Exception as e: self.log(f"❌ Автозагрузка қатесі: {e}")

    def alert_thread(self, message):
        def send():
            if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return
            try: requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", 
                               data={"chat_id": TELEGRAM_CHAT_ID, "text": f"🛡️ *QYRAGY KOZ GLOBAL 4.0*\n\n{message}", "parse_mode": "Markdown"}, timeout=10)
            except: pass
        threading.Thread(target=send, daemon=True).start()

    def log(self, message):
        try:
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            if hasattr(self, 'log_box'):
                self.log_box.insert("end", f"[{ts}] {message}\n")
                self.log_box.see("end")
        except: pass

    def move_to_quarantine(self, file_path, reason="Malicious"):
        """ Файлды дискілер арасында қауіпсіз көшіру (WinError 5 және 17 түзетілген) """
        try:
            dest = os.path.join(QUARANTINE_FOLDER, f"{int(time.time())}_{os.path.basename(file_path)}")
            # Рұқсаттарды (Read-only) алып тастау
            win32api.SetFileAttributes(file_path, win32con.FILE_ATTRIBUTE_NORMAL)
            shutil.copy2(file_path, dest) 
            if os.path.isdir(file_path): shutil.rmtree(file_path)
            else: os.remove(file_path) 
            self.alert_thread(f"‼️ *ҚАУІПТІ ФАЙЛ:* `{os.path.basename(file_path)}` \n📥 Карантинге көшірілді.")
            return True
        except Exception as e: self.log(f"❌ Карантин қатесі: {e}"); return False

    def start_vaccine(self):
        threading.Thread(target=self.vaccine_process, daemon=True).start()

    def vaccine_process(self):
        """ Вакцинация логикасы мен логқа ақпарат шығару """
        drives = self.get_drives()
        if not drives:
            self.log("❌ Вакцинация: USB табылмады.")
            return
        for drive in drives:
            target = os.path.join(drive, "autorun.inf")
            try:
                if not os.path.exists(target):
                    os.makedirs(target)
                    os.system(f'attrib +s +h +r "{target}"')
                    self.log(f"✅ Вакцинация: {drive} қорғалды.")
                    self.alert_thread(f"💉 Вакцинация: {drive} қорғалды.")
                else:
                    self.log(f"ℹ️ Вакцинация: {drive} бұрыннан қорғалған.")
            except Exception as e: self.log(f"❌ Вакцинация қатесі: {e}")

    def start_scan_all(self):
        threading.Thread(target=self.scan_process, daemon=True).start()

    def scan_process(self):
        drives = self.get_drives()
        for drive in drives:
            try:
                for item in os.listdir(drive):
                    path = os.path.join(drive, item)
                    if item.lower() == "autorun.inf" or os.path.splitext(item)[1].lower() in DANGEROUS_EXTENSIONS:
                        self.move_to_quarantine(path, "Virus detection")
            except: pass
        self.log(TRANSLATIONS[self.current_lang]["msg_done"])

    def kill_virus_processes(self):
        targets = ["wscript.exe", "cscript.exe", "powershell.exe", "cmd.exe"]
        for proc in targets: os.system(f'taskkill /f /im {proc} >nul 2>&1')
        self.log("🧹 Процестер тазаланды."); self.alert_thread("🧹 Процестер тазаланды.")

    def get_drives(self):
        drives = []
        try:
            for drive in win32api.GetLogicalDriveStrings().split('\000')[:-1]:
                if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE: drives.append(drive)
        except: pass
        return drives

    def usb_monitor_loop(self):
        last_drives = self.get_drives()
        while self.monitoring:
            current = self.get_drives()
            if len(current) > len(last_drives):
                new = list(set(current) - set(last_drives))
                self.alert_thread(f"🔌 *Жаңа USB:* {new[0]}")
                # Жаңа диск қосылғанда автоматты вакцинация
                self.after(0, lambda d=new[0]: self.vaccinate_drive_auto(d))
            last_drives = current; time.sleep(3)

    def vaccinate_drive_auto(self, drive):
        target = os.path.join(drive, "autorun.inf")
        if not os.path.exists(target):
            try:
                os.makedirs(target)
                os.system(f'attrib +s +h +r "{target}"')
                self.log(f"🛡️ Авто-Вакцинация: {drive} қорғалды.")
            except: pass

    def hid_monitor_loop(self):
        pythoncom.CoInitialize()
        c = wmi.WMI()
        watcher = c.Win32_Keyboard.watch_for("creation")
        while self.monitoring:
            try:
                device = watcher()
                pnp = getattr(device, "PNPDeviceID", "Unknown")
                if pnp not in self.allowed_keyboards:
                    self.alert_thread("🚨 *HID ALERT!* Белгісіз клавиатура анықталды.")
                    if self.paranoid_var.get(): os.system("rundll32.exe user32.dll,LockWorkStation")
            except: pass

    def setup_tray(self):
        try:
            image = Image.open(ICON_PATH) if os.path.exists(ICON_PATH) else Image.new('RGB', (64, 64), (0, 128, 255))
            self.icon = pystray.Icon("Qyragy Koz", image, "Qyragy Koz", (item('Open', self.show_window), item('Exit', self.quit_app)))
            self.icon.run()
        except: pass

    def load_allowlist(self):
        if os.path.exists(ALLOW_LIST_FILE):
            with open(ALLOW_LIST_FILE, "r") as f: return set(json.load(f))
        return set()

    def start_notification(self):
        self.alert_thread("🚀 *Жүйе бақылауды бастады!*")

    def hide_window(self): self.withdraw()
    def show_window(self, icon, item): self.icon.stop(); self.after(0, self.deiconify); threading.Thread(target=self.setup_tray, daemon=True).start()
    def quit_app(self, icon, item): self.icon.stop(); self.monitoring = False; os._exit(0)

if __name__ == "__main__":
    app = QyragyKozApp()
    app.mainloop()