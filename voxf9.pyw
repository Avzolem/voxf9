# -*- coding: utf-8 -*-
"""
VoxF9 - Transcripción de voz en tiempo real
Presiona F9 para activar/desactivar
"""

import os
import sys
import threading

# Configuración
SAMPLE_RATE = 16000
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip"
MODEL_NAME = "vosk-model-es-0.42"
TOGGLE_KEY = "f9"

def get_app_path():
    """Obtiene la ruta de la aplicación"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_PATH = get_app_path()
MODEL_PATH = os.path.join(APP_PATH, "model")
SHORTCUTS_CREATED_FLAG = os.path.join(APP_PATH, ".shortcuts_created")

def create_shortcuts():
    """Crea accesos directos en el escritorio, carpeta de instalación y desinstalador"""
    if os.path.exists(SHORTCUTS_CREATED_FLAG):
        return

    try:
        import subprocess
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        icon_path = os.path.join(APP_PATH, "icon.ico")
        uninstall_bat = os.path.join(APP_PATH, "Desinstalar.bat")

        if not os.path.exists(icon_path):
            icon_path = exe_path

        # Crear Desinstalar.bat si no existe
        if not os.path.exists(uninstall_bat):
            uninstall_content = '''@echo off
title Desinstalar VoxF9
echo.
echo ========================================
echo   DESINSTALAR VOXF9
echo ========================================
echo.
echo Esto eliminara:
echo   - VoxF9.exe
echo   - Modelo de voz (1.4 GB)
echo   - Acceso directo del escritorio
echo.
set /p confirm="Estas seguro? (S/N): "
if /i not "%confirm%"=="S" goto :cancel

echo.
echo [1/3] Cerrando VoxF9...
taskkill /f /im VoxF9.exe >nul 2>&1
timeout /t 2 >nul

echo [2/3] Eliminando acceso directo...
del "%USERPROFILE%\\Desktop\\VoxF9.lnk" 2>nul

echo [3/3] Eliminando archivos del programa...
set "FOLDER=%~dp0"

:: Auto-eliminar la carpeta
start /b "" cmd /c "timeout /t 2 >nul & rmdir /s /q "%FOLDER%""

echo.
echo ========================================
echo   VoxF9 desinstalado correctamente
echo ========================================
echo.
echo La ventana se cerrara automaticamente...
timeout /t 3 >nul
exit

:cancel
echo.
echo Desinstalacion cancelada.
pause
'''
            with open(uninstall_bat, 'w', encoding='utf-8') as f:
                f.write(uninstall_content)

        # Script PowerShell para crear accesos directos
        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell

# Acceso directo en el escritorio
$DesktopShortcut = $WshShell.CreateShortcut("$env:USERPROFILE\\Desktop\\VoxF9.lnk")
$DesktopShortcut.TargetPath = "{exe_path}"
$DesktopShortcut.WorkingDirectory = "{APP_PATH}"
$DesktopShortcut.IconLocation = "{icon_path}"
$DesktopShortcut.Description = "VoxF9 - Voz a texto con F9"
$DesktopShortcut.Save()

# Acceso directo en la carpeta de instalación
$FolderShortcut = $WshShell.CreateShortcut("{APP_PATH}\\VoxF9.lnk")
$FolderShortcut.TargetPath = "{exe_path}"
$FolderShortcut.WorkingDirectory = "{APP_PATH}"
$FolderShortcut.IconLocation = "{icon_path}"
$FolderShortcut.Description = "VoxF9 - Voz a texto con F9"
$FolderShortcut.Save()

# Acceso directo del desinstalador con icono de papelera
$UninstallShortcut = $WshShell.CreateShortcut("{APP_PATH}\\Desinstalar VoxF9.lnk")
$UninstallShortcut.TargetPath = "{uninstall_bat}"
$UninstallShortcut.WorkingDirectory = "{APP_PATH}"
$UninstallShortcut.IconLocation = "shell32.dll,31"
$UninstallShortcut.Description = "Desinstalar VoxF9 del equipo"
$UninstallShortcut.Save()
'''
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            creationflags=0x08000000
        )
        with open(SHORTCUTS_CREATED_FLAG, 'w') as f:
            f.write('1')
    except Exception:
        pass


class ModelDownloader:
    """Descarga el modelo con barra de progreso"""

    def __init__(self):
        self.root = None
        self.progress = None
        self.label = None
        self.cancelled = False

    def download_with_progress(self):
        """Muestra ventana de descarga"""
        import tkinter as tk
        from tkinter import ttk

        self.root = tk.Tk()
        self.root.title("VoxF9 - Descargando modelo")
        self.root.geometry("450x120")
        self.root.resizable(False, False)
        self.root.eval('tk::PlaceWindow . center')

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(frame, text="Descargando modelo de voz (1.4 GB)...")
        self.label.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(frame, length=400, mode='determinate')
        self.progress.pack(pady=(0, 10))

        self.status = ttk.Label(frame, text="Iniciando...")
        self.status.pack()

        threading.Thread(target=self._download, daemon=True).start()
        self.root.mainloop()
        return not self.cancelled

    def _download(self):
        """Descarga el archivo"""
        import zipfile
        import urllib.request

        zip_path = os.path.join(APP_PATH, "model.zip")

        try:
            def progress_hook(count, block_size, total_size):
                if self.cancelled:
                    return
                percent = int(count * block_size * 100 / total_size)
                downloaded = count * block_size / (1024 * 1024)
                total = total_size / (1024 * 1024)
                self.root.after(0, lambda: self._update_progress(percent, downloaded, total))

            urllib.request.urlretrieve(MODEL_URL, zip_path, progress_hook)

            if self.cancelled:
                return

            self.root.after(0, lambda: self.label.config(text="Extrayendo modelo..."))
            self.root.after(0, lambda: self.progress.config(mode='indeterminate'))
            self.root.after(0, lambda: self.progress.start())

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(APP_PATH)

            extracted_path = os.path.join(APP_PATH, MODEL_NAME)
            if os.path.exists(MODEL_PATH):
                import shutil
                shutil.rmtree(MODEL_PATH)
            os.rename(extracted_path, MODEL_PATH)

            os.remove(zip_path)
            self.root.after(0, self.root.destroy)

        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))

    def _update_progress(self, percent, downloaded, total):
        self.progress['value'] = percent
        self.status.config(text=f"{downloaded:.1f} MB / {total:.1f} MB ({percent}%)")

    def _show_error(self, error):
        self.label.config(text=f"Error: {error}")
        self.cancelled = True


def ensure_model():
    """Verifica que el modelo existe, si no lo descarga"""
    if not os.path.exists(MODEL_PATH):
        downloader = ModelDownloader()
        if not downloader.download_with_progress():
            sys.exit(1)


def main():
    ensure_model()

    # Imports ligeros primero para mostrar icono rápido
    from PIL import Image, ImageDraw
    import pystray

    def create_icon_image(active=False, loading=False):
        """Crea ícono de micrófono"""
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if loading:
            bg_color = '#FFA726'  # Naranja = cargando
        elif active:
            bg_color = '#4CAF50'  # Verde = activo
        else:
            bg_color = '#607D8B'  # Gris = inactivo

        draw.ellipse([2, 2, size-2, size-2], fill=bg_color)

        white = '#FFFFFF'
        cap_left, cap_right = 22, 42
        cap_top, cap_bottom = 12, 38

        draw.ellipse([cap_left, cap_top, cap_right, cap_top + 20], fill=white)
        draw.rectangle([cap_left, cap_top + 10, cap_right, cap_bottom], fill=white)
        draw.arc([16, 28, 48, 52], 0, 180, fill=white, width=3)
        draw.rectangle([31, 46, 33, 54], fill=white)
        draw.rectangle([24, 52, 40, 55], fill=white)

        return img

    class VoxF9:
        def __init__(self):
            self.is_listening = False
            self.is_running = True
            self.is_ready = False
            self.audio_queue = None
            self.model = None
            self.recognizer = None
            self.icon = None
            self.last_partial = ""
            self.chars_written = 0
            self.lock = threading.Lock()
            self.stream = None
            # Módulos cargados después
            self.pyautogui = None
            self.keyboard = None
            self.sd = None
            self.winsound = None
            self.json = None
            self.KaldiRecognizer = None

        def load_all(self):
            """Carga todos los módulos pesados en segundo plano"""
            import queue
            import json
            import pyautogui
            import keyboard
            from vosk import Model, KaldiRecognizer, SetLogLevel
            import sounddevice as sd
            import winsound

            SetLogLevel(-1)
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0

            self.audio_queue = queue.Queue(maxsize=50)
            self.json = json
            self.pyautogui = pyautogui
            self.keyboard = keyboard
            self.sd = sd
            self.winsound = winsound
            self.KaldiRecognizer = KaldiRecognizer

            # Cargar modelo (lo más pesado)
            self.model = Model(MODEL_PATH)
            self.reset_recognizer()

            # Configurar hotkey
            self.keyboard.on_press_key(TOGGLE_KEY, lambda _: self.toggle_listening(), suppress=False)

            # Iniciar stream de audio
            self.stream = self.sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=2000,
                dtype='int16',
                channels=1,
                callback=self.audio_callback
            )
            self.stream.start()

            # Iniciar procesador de audio
            threading.Thread(target=self.process_audio, daemon=True).start()

            # Marcar como listo y actualizar icono
            self.is_ready = True
            if self.icon:
                self.icon.icon = create_icon_image(False, False)
                self.icon.title = "VoxF9 - Listo (F9)"

            # Crear shortcuts en background (no crítico)
            threading.Thread(target=create_shortcuts, daemon=True).start()

        def reset_recognizer(self):
            self.recognizer = self.KaldiRecognizer(self.model, SAMPLE_RATE)
            self.recognizer.SetWords(False)

        def audio_callback(self, indata, frames, time_info, status):
            if self.is_listening and self.audio_queue:
                try:
                    self.audio_queue.put_nowait(bytes(indata))
                except:
                    pass

        def write_fast(self, text):
            if not text:
                return
            try:
                import pyperclip
                pyperclip.copy(text)
                self.pyautogui.hotkey('ctrl', 'v')
            except:
                self.pyautogui.write(text, interval=0.005)

        def delete_chars(self, count):
            if count > 0:
                self.pyautogui.press('backspace', presses=count, interval=0.003)

        def process_audio(self):
            import time
            while self.is_running:
                if not self.is_listening:
                    if self.audio_queue:
                        while not self.audio_queue.empty():
                            try:
                                self.audio_queue.get_nowait()
                            except:
                                break
                    time.sleep(0.05)
                    continue

                try:
                    data = self.audio_queue.get(timeout=0.03)

                    with self.lock:
                        if self.recognizer.AcceptWaveform(data):
                            result = self.json.loads(self.recognizer.Result())
                            text = result.get('text', '').strip()

                            if text:
                                self.delete_chars(self.chars_written)
                                self.write_fast(text + ' ')
                                self.chars_written = 0
                                self.last_partial = ""
                        else:
                            partial = self.json.loads(self.recognizer.PartialResult())
                            partial_text = partial.get('partial', '').strip()

                            if partial_text and partial_text != self.last_partial:
                                self.delete_chars(self.chars_written)
                                self.write_fast(partial_text)
                                self.chars_written = len(partial_text)
                                self.last_partial = partial_text

                except:
                    pass

        def toggle_listening(self):
            if not self.is_ready:
                return

            with self.lock:
                self.is_listening = not self.is_listening
                self.last_partial = ""
                self.chars_written = 0

                if self.is_listening:
                    self.reset_recognizer()
                    while self.audio_queue and not self.audio_queue.empty():
                        try:
                            self.audio_queue.get_nowait()
                        except:
                            break

            self.update_icon()
            freq = 800 if self.is_listening else 400
            threading.Thread(target=lambda: self.winsound.Beep(freq, 80), daemon=True).start()

        def update_icon(self):
            if self.icon:
                self.icon.icon = create_icon_image(self.is_listening, False)
                status = "ACTIVO" if self.is_listening else "Inactivo"
                self.icon.title = f"VoxF9 - {status}"

        def quit_app(self, icon=None, item=None):
            self.is_running = False
            self.is_listening = False

            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                except:
                    pass

            if icon:
                try:
                    icon.stop()
                except:
                    pass

            os._exit(0)

        def toggle_from_menu(self, icon=None, item=None):
            if self.is_ready:
                self.toggle_listening()

        def get_status_text(self, item):
            if not self.is_ready:
                return "Cargando..."
            return "Desactivar (F9)" if self.is_listening else "Activar (F9)"

        def run(self):
            # Cargar módulos pesados en segundo plano
            threading.Thread(target=self.load_all, daemon=True).start()

            menu = pystray.Menu(
                pystray.MenuItem(self.get_status_text, self.toggle_from_menu, default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Salir", self.quit_app)
            )

            # Mostrar icono inmediatamente (naranja = cargando)
            self.icon = pystray.Icon(
                name="VoxF9",
                icon=create_icon_image(False, True),
                title="VoxF9 - Cargando...",
                menu=menu
            )

            self.icon.run()

    app = VoxF9()
    app.run()

if __name__ == "__main__":
    main()
