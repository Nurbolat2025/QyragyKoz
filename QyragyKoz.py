import customtkinter as ctk
import os
import shutil
import time
import datetime
import threading
import sys
import hashlib
import requests
from PIL import Image
import pystray
from pystray import MenuItem as item
import win32api
import win32file
import win32con

# --- БАПТАУЛАР / SETTINGS ---
# Пайдаланушы назарына: Программа істеуі үшін төменге өз деректеріңізді жазыңыз.
# Notice: To run the program, please enter your own credentials below.

TELEGRAM_BOT_TOKEN = "YOUR_TOKEN_HERE"  
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"  
VIRUSTOTAL_API_KEY = "YOUR_API_KEY_HERE" 

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

QUARANTINE_FOLDER = r"C:\QyragyKoz_Quarantine"
LOG_FILE = os.path.join(QUARANTINE_FOLDER, "scan_log.txt")
DANGEROUS_EXTENSIONS = ['.lnk', '.vbs', '.bat', '.cmd', '.scr', '.pif', '.wsf', '.js', '.jse']
AUTORUN_FILE = "autorun.inf"
ICON_PATH = "QyragyKoz.ico"

# --- АУДАРМАЛАР (TRANSLATIONS) ---
TRANSLATIONS = {
    "KZ": {
        "title": "QYRAGY KOZ\n🛡️ GLOBAL",
        "scan": "ТОЛЫҚ ТЕКСЕРУ",
        "vaccine": "💉 Вакцинация жасау",
        "quarantine": "Карантинді ашу",
        "kill": "Вирус процесті жою",
        "status": "Жүйе күту режимінде...",
        "lang": "Тіл / Language:",
        "log_start": "Бағдарлама іске қосылды.",
        "msg_new_usb": "⚡ Жаңа USB табылды:",
        "msg_virus": "Вирус табылды!",
        "msg_clean": "Флешка таза.",
        "msg_done": "Аяқталды!"
    },
    "EN": {
        "title": "QYRAGY KOZ\n🛡️ GLOBAL",
        "scan": "FULL SCAN",
        "vaccine": "💉 Vaccinate USB",
        "quarantine": "Open Quarantine",
        "kill": "Kill Virus Processes",
        "status": "System is idle...",
        "lang": "Language:",
        "log_start": "Program started.",
        "msg_new_usb": "⚡ New USB detected:",
        "msg_virus": "Virus found!",
        "msg_clean": "USB is clean.",
        "msg_done": "Finished!"
    },
    "RU": {
        "title": "QYRAGY KOZ\n🛡️ GLOBAL",
        "scan": "ПОЛНОЕ СКАНИРОВАНИЕ",
        "vaccine": "💉 Вакцинация USB",
        "quarantine": "Открыть карантин",
        "kill": "Убить процессы вируса",
        "status": "Система в ожидании...",
        "lang": "Язык / Language:",
        "log_start": "Программа запущена.",
        "msg_new_usb": "⚡ Обнаружен USB:",
        "msg_virus": "Найден вирус!",
        "msg_clean": "Флешка чиста.",
        "msg_done": "Готово!"
    }
}

class QyragyKozApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QYRAGY KOZ GLOBAL 4.0")
        self.geometry("800x600")
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', self.hide_window)

        if os.path.exists(ICON_PATH):
            try: self.iconbitmap(ICON_PATH)
            except: pass

        if not os.path.exists(QUARANTINE_FOLDER):
            os.makedirs(QUARANTINE_FOLDER)
            
        self.current_lang = "KZ" # Default Language

        self.setup_ui()
        
        self.tray_thread = threading.Thread(target=self.setup_tray, daemon=True)
        self.tray_thread.start()

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.usb_monitor_loop, daemon=True)
        self.monitor_thread.start()

    def setup_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar, text=TRANSLATIONS[self.current_lang]["title"], font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=(20, 10))

        # Language Menu
        self.lbl_lang = ctk.CTkLabel(self.sidebar, text=TRANSLATIONS[self.current_lang]["lang"], font=ctk.CTkFont(size=12))
        self.lbl_lang.pack(pady=(10, 0))
        
        self.lang_menu = ctk.CTkOptionMenu(self.sidebar, values=["KZ", "EN", "RU"], command=self.change_language)
        self.lang_menu.pack(padx=20, pady=5)
        self.lang_menu.set("KZ")

        # Buttons
        self.btn_scan_all = ctk.CTkButton(self.sidebar, text=TRANSLATIONS[self.current_lang]["scan"], fg_color="green", hover_color="darkgreen", command=self.start_scan_all)
        self.btn_scan_all.pack(padx=20, pady=10)

        self.btn_vaccine = ctk.CTkButton(self.sidebar, text=TRANSLATIONS[self.current_lang]["vaccine"], fg_color="#D35400", hover_color="#A04000", command=self.start_vaccine)
        self.btn_vaccine.pack(padx=20, pady=10)

        self.btn_quarantine = ctk.CTkButton(self.sidebar, text=TRANSLATIONS[self.current_lang]["quarantine"], command=self.open_quarantine)
        self.btn_quarantine.pack(padx=20, pady=10)
        
        self.btn_kill = ctk.CTkButton(self.sidebar, text=TRANSLATIONS[self.current_lang]["kill"], fg_color="red", hover_color="darkred", command=self.kill_virus_processes)
        self.btn_kill.pack(padx=20, pady=10)

        # Main Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.lbl_status = ctk.CTkLabel(self.main_frame, text=TRANSLATIONS[self.current_lang]["status"], font=ctk.CTkFont(size=14))
        self.lbl_status.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self.main_frame, orientation="horizontal")
        self.progress.pack(fill="x", padx=20, pady=5)
        self.progress.set(0)

        self.log_box = ctk.CTkTextbox(self.main_frame, width=400, height=300)
        self.log_box.pack(padx=10, pady=10, fill="both", expand=True)
        self.log(TRANSLATIONS[self.current_lang]["log_start"])

    def change_language(self, new_lang):
        self.current_lang = new_lang
        t = TRANSLATIONS[new_lang]
        
        self.logo_label.configure(text=t["title"])
        self.lbl_lang.configure(text=t["lang"])
        self.btn_scan_all.configure(text=t["scan"])
        self.btn_vaccine.configure(text=t["vaccine"])
        self.btn_quarantine.configure(text=t["quarantine"])
        self.btn_kill.configure(text=t["kill"])
        self.lbl_status.configure(text=t["status"])
        self.log(f"Language changed to {new_lang}")

    # --- LOGIC METHODS (БҰРЫН ЖОҒАЛЫП ҚАЛҒАНДАР) ---

    def log(self, message):
        try:
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            self.log_box.insert("end", f"[{ts}] {message}\n")
            self.log_box.see("end")
        except: pass

    def is_safe_drive_structure(self, drive_path):
        safe_folders = ["efi", "boot", "sources", "support", "en-us"]
        try:
            items = [i.lower() for i in os.listdir(drive_path) if os.path.isdir(os.path.join(drive_path, i))]
            for folder in safe_folders:
                if folder in items: return True
        except: pass
        return False

    def is_malicious_autorun(self, file_path):
        try:
            with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                content = f.read().lower()
            if "setup.exe" in content or "install.exe" in content: return False 
            if "icon=" in content and "open=" not in content and "shellexecute=" not in content: return False
            suspicious_keywords = ["open=", "shellexecute=", "shell\\open\\command="]
            dangerous_targets = [".vbs", ".js", ".cmd", ".bat", ".lnk", "recycler", "system volume information"]
            for key in suspicious_keywords:
                if key in content:
                    for target in dangerous_targets:
                        if target in content: return True
                    return True 
        except: pass
        return False

    def send_telegram_alert(self, message):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🛡️ QYRAGY KOZ:\n{message}"}
            requests.post(url, data=data)
        except: pass

    def check_virustotal(self, file_path):
        if not VIRUSTOTAL_API_KEY: return None
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            file_hash = sha256_hash.hexdigest()
            url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
            headers = {"x-apikey": VIRUSTOTAL_API_KEY}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                stats = response.json()['data']['attributes']['last_analysis_stats']
                if stats['malicious'] > 0:
                    return f"⚠️ VIRUSTOTAL: {stats['malicious']} detections!"
        except: return None
        return None

    def move_to_quarantine(self, file_path, reason="Unknown"):
        try:
            filename = os.path.basename(file_path)
            new_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            dest_path = os.path.join(QUARANTINE_FOLDER, new_name)
            shutil.move(file_path, dest_path)
            threading.Thread(target=self.send_telegram_alert, args=(f"Virus: {filename}\nReason: {reason}",), daemon=True).start()
            return True
        except: return False

    def unhide_file(self, path):
        try:
            attrs = win32api.GetFileAttributes(path)
            if attrs & win32con.FILE_ATTRIBUTE_HIDDEN or attrs & win32con.FILE_ATTRIBUTE_SYSTEM:
                win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_NORMAL)
                return True
        except: pass
        return False

    def get_drives(self):
        drives = []
        try:
            drive_list = win32api.GetLogicalDriveStrings().split('\000')[:-1]
            for drive in drive_list:
                if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
                    drives.append(drive)
        except: pass
        return drives

    def vaccinate_drive(self, drive_path):
        if self.is_safe_drive_structure(drive_path): return False
        target = os.path.join(drive_path, AUTORUN_FILE)
        try:
            if os.path.isfile(target):
                if self.is_malicious_autorun(target):
                    os.chmod(target, 0o777)
                    os.remove(target)
                else: return True 
            if not os.path.exists(target):
                os.makedirs(target)
                os.system(f'attrib +s +h +r "{target}"')
                return True
        except: pass
        return False

    def open_quarantine(self):
        os.startfile(QUARANTINE_FOLDER)

    def kill_virus_processes(self):
        self.log(TRANSLATIONS[self.current_lang]["kill"] + "...")
        targets = ["wscript.exe", "cscript.exe", "powershell.exe", "cmd.exe"]
        count = 0
        for proc in targets:
            if os.system(f'taskkill /f /im {proc}') == 0: count += 1
        self.log(f"Killed {count} processes.")

    def start_scan_all(self):
        threading.Thread(target=self.scan_process, daemon=True).start()

    def start_vaccine(self):
        threading.Thread(target=self.vaccine_process, daemon=True).start()

    def vaccine_process(self):
        drives = self.get_drives()
        for drive in drives:
            if self.vaccinate_drive(drive): self.log(f"✅ {drive} Vaccinated")
            else: self.log(f"ℹ️ {drive} Skipped")

    def scan_process(self):
        drives = self.get_drives()
        if not drives:
            self.log("No USB found.")
            return

        self.btn_scan_all.configure(state="disabled")
        self.progress.set(0)
        
        for drive in drives:
            self.log(f"Scanning {drive}...")
            if self.is_safe_drive_structure(drive):
                 self.log(f"Skipping bootable drive: {drive}")
            
            try:
                root_files = os.listdir(drive)
                total = len(root_files)
                for i, item in enumerate(root_files):
                    path = os.path.join(drive, item)
                    if total > 0: self.progress.set((i+1)/total)

                    # Scan Logic
                    if item.lower() == AUTORUN_FILE:
                        if os.path.isfile(path) and self.is_malicious_autorun(path):
                            self.move_to_quarantine(path, "Malicious Autorun")
                    
                    ext = os.path.splitext(item)[1].lower()
                    if os.path.isfile(path) and ext in DANGEROUS_EXTENSIONS:
                        self.move_to_quarantine(path, f"Dangerous Ext {ext}")
                    
                    if os.path.isfile(path) and ext == ".exe":
                        if "setup" not in item.lower() and "install" not in item.lower():
                            res = self.check_virustotal(path)
                            if res: 
                                self.log(res)
                                self.move_to_quarantine(path, "VirusTotal")

                    if os.path.isdir(path):
                        if item.lower() not in ["boot", "efi", "sources"]:
                            self.unhide_file(path)
                        
                        # Fake Folder check
                        exe_virus = path + ".exe"
                        if os.path.exists(exe_virus) and os.path.isfile(exe_virus):
                            self.move_to_quarantine(exe_virus, "Fake Folder")

            except Exception as e: self.log(f"Error: {e}")

        self.progress.set(1)
        self.log(TRANSLATIONS[self.current_lang]["msg_done"])
        self.btn_scan_all.configure(state="normal")

    def usb_monitor_loop(self):
        last_drives = self.get_drives()
        while self.monitoring:
            current = self.get_drives()
            if len(current) > len(last_drives):
                new = list(set(current) - set(last_drives))
                self.log(f"{TRANSLATIONS[self.current_lang]['msg_new_usb']} {new}")
                self.after(0, self.deiconify)
                self.vaccinate_drive(new[0])
            last_drives = current
            time.sleep(3)

    def setup_tray(self):
        image = Image.open(ICON_PATH) if os.path.exists(ICON_PATH) else Image.new('RGB', (64, 64), (73, 109, 137))
        menu = (item('Open', self.show_window), item('Exit', self.quit_app))
        self.icon = pystray.Icon("Qyragy Koz", image, "Qyragy Koz", menu)
        self.icon.run()

    def hide_window(self):
        self.withdraw()
        
    def show_window(self, icon, item):
        self.icon.stop() 
        self.after(0, self.deiconify)
        threading.Thread(target=self.setup_tray, daemon=True).start()

    def quit_app(self, icon, item):
        self.icon.stop()
        self.monitoring = False
        self.quit()
        sys.exit()

if __name__ == "__main__":
    app = QyragyKozApp()
    app.mainloop()