<p align="center">
  <img src="QyragyKoz.ico" width="100" height="100" alt="QyragyKoz Logo">
</p>

# 🛡️ Qyragy Koz - Smart USB Antivirus

[![Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Made in](https://img.shields.io/badge/Made%20in-Kazakhstan-cyan.svg)](https://github.com/topics/kazakhstan)

**Languages:** [🇺🇸 English](#-english) | [🇰🇿 Қазақша](#-қазақша) | [🇷🇺 Русский](#-русский)

---

## 🇺🇸 English

**Qyragy Koz** is an open-source USB security tool designed to protect computers from autorun viruses, shortcuts (.lnk), and hidden malware. It features **VirusTotal** integration for cloud scanning and sends real-time alerts via **Telegram**.

### ✨ Key Features
* **Auto-Scan:** Automatically detects and scans connected USB drives.
* **Vaccination:** Creates a protected `autorun.inf` folder to prevent future infections.
* **Smart Detection:** Identifies malicious scripts (.vbs, .bat) and "Fake Folder" viruses (.exe).
* **VirusTotal Integration:** Checks suspicious file hashes against 70+ antiviruses.
* **Telegram Alerts:** Sends notifications to your phone when a virus is found.
* **Hidden Files Restore:** Unhides folders that were hidden by viruses.
* **Process Killer:** Terminates malicious processes (wscript, cscript) running in memory.

### 🚀 How to Run
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/QyragyKoz.git](https://github.com/YOUR_USERNAME/QyragyKoz.git)
    cd QyragyKoz
    ```
2.  **Install dependencies:**
    ```bash
    pip install customtkinter pystray pillow requests pywin32
    ```
3.  **Configure Keys:**
    * Open `QyragyKoz.py`.
    * Find the **SETTINGS** section at the top.
    * Enter your `TELEGRAM_BOT_TOKEN`, `CHAT_ID`, and `VIRUSTOTAL_API_KEY`.
4.  **Run:**
    ```bash
    python QyragyKoz.py
    ```

---

## 🇰🇿 Қазақша

**Qyragy Koz (Қырағы Көз)** — USB флешкалар арқылы тарайтын вирустардан қорғайтын ашық кодты бағдарлама. Ол компьютерді "Autorun" вирустарынан, жасырын жапсырмалардан (.lnk) қорғайды және күдікті файлдарды **VirusTotal** базасы арқылы тексереді.

### ✨ Ерекшеліктері
* **Автоматты тексеру:** Флешка қосылған сәтте оны бірден тексереді.
* **Вакцинация:** Флешкаға өшпейтін арнайы `autorun.inf` папкасын орнатып, вирус кіруіне жол бермейді.
* **VirusTotal интеграциясы:** Күдікті `.exe` файлдарды интернет арқылы әлемдік базадан тексереді.
* **Telegram хабарлама:** Вирус табылса, телефоныңызға бірден хабарлама келеді.
* **Файлдарды емдеу:** Вирус жасырып тастаған папкаларды қайтадан ашады.
* **Көптілді интерфейс:** Қазақ, Ағылшын және Орыс тілдерін қолдайды.

### 🚀 Қалай қосу керек?
1.  **Жүктеп алыңыз:** Кодты компьютерге жүктеңіз.
2.  **Кітапханаларды орнатыңыз:**
    `pip install customtkinter pystray pillow requests pywin32`
3.  **Баптау:**
    * `QyragyKoz.py` файлын ашыңыз.
    * Ішіндегі `SETTINGS` бөліміне Telegram және VirusTotal кілттерін жазыңыз.
4.  **Іске қосу:** `python QyragyKoz.py` командасын теріңіз.

---

## 🇷🇺 Русский

**Qyragy Koz** — это инструмент для защиты USB-носителей с открытым исходным кодом. Программа защищает от вирусов автозапуска, скрытых майнеров и троянов. Поддерживает облачное сканирование через **VirusTotal** и уведомления в **Telegram**.

### ✨ Возможности
* **Авто-сканирование:** Мониторинг подключенных USB-устройств.
* **Вакцинация:** Создание нестираемой папки `autorun.inf` для блокировки вирусов.
* **Восстановление файлов:** Возвращает видимость скрытым папкам.
* **Умная защита:** Анализ содержимого файлов автозапуска.
* **Уведомления:** Отправка отчетов в Telegram-бот.

### 🚀 Запуск
1.  Скачайте архив или клонируйте репозиторий.
2.  Установите библиотеки: `pip install -r requirements.txt` (или вручную).
3.  Впишите свои API ключи в файл `QyragyKoz.py`.
4.  Запустите файл.

---

### ⚠️ Disclaimer / Ескерту
This software is provided "as is", without warranty of any kind. Use it at your own risk.
Бұл бағдарлама "бар күйінде" ұсынылады. Автор пайдалану нәтижелеріне жауапкершілік алмайды.

**Created with ❤️ in Kazakhstan**