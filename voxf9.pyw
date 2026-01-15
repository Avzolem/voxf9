# -*- coding: utf-8 -*-
"""
VoxF9 - Transcripción de voz en tiempo real
Presiona F9 para activar/desactivar
"""

import os
import sys
import json
import threading
import queue
import time
import zipfile
import urllib.request
import tkinter as tk
from tkinter import ttk

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

class ModelDownloader:
    """Descarga el modelo con barra de progreso"""

    def __init__(self):
        self.root = None
        self.progress = None
        self.label = None
        self.cancelled = False

    def download_with_progress(self):
        """Muestra ventana de descarga"""
        self.root = tk.Tk()
        self.root.title("VoxF9 - Descargando modelo")
        self.root.geometry("450x120")
        self.root.resizable(False, False)

        # Centrar ventana
        self.root.eval('tk::PlaceWindow . center')

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(frame, text="Descargando modelo de voz (1.4 GB)...")
        self.label.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(frame, length=400, mode='determinate')
        self.progress.pack(pady=(0, 10))

        self.status = ttk.Label(frame, text="Iniciando...")
        self.status.pack()

        # Iniciar descarga en thread
        threading.Thread(target=self._download, daemon=True).start()

        self.root.mainloop()
        return not self.cancelled

    def _download(self):
        """Descarga el archivo"""
        zip_path = os.path.join(APP_PATH, "model.zip")

        try:
            # Descargar
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

            # Extraer
            self.root.after(0, lambda: self.label.config(text="Extrayendo modelo..."))
            self.root.after(0, lambda: self.progress.config(mode='indeterminate'))
            self.root.after(0, lambda: self.progress.start())

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(APP_PATH)

            # Renombrar carpeta
            extracted_path = os.path.join(APP_PATH, MODEL_NAME)
            if os.path.exists(MODEL_PATH):
                import shutil
                shutil.rmtree(MODEL_PATH)
            os.rename(extracted_path, MODEL_PATH)

            # Limpiar
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


# Importar después de verificar modelo (para que el splash sea primero)
def main():
    ensure_model()

    import pyautogui
    import keyboard
    from vosk import Model, KaldiRecognizer, SetLogLevel
    import sounddevice as sd
    from PIL import Image, ImageDraw
    import pystray
    import winsound

    # Silenciar logs de Vosk
    SetLogLevel(-1)

    # Optimizar pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0

    class VoxF9:
        def __init__(self):
            self.is_listening = False
            self.is_running = True
            self.audio_queue = queue.Queue(maxsize=50)
            self.model = None
            self.recognizer = None
            self.icon = None
            self.last_partial = ""
            self.chars_written = 0
            self.lock = threading.Lock()
            self.stream = None

        def load_model(self):
            self.model = Model(MODEL_PATH)
            self.reset_recognizer()

        def reset_recognizer(self):
            self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
            self.recognizer.SetWords(False)

        def create_icon(self, active=False):
            """Crea ícono de micrófono"""
            size = 64
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            bg_color = '#4CAF50' if active else '#607D8B'
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

        def audio_callback(self, indata, frames, time_info, status):
            if self.is_listening:
                try:
                    self.audio_queue.put_nowait(bytes(indata))
                except queue.Full:
                    pass

        def write_fast(self, text):
            if not text:
                return
            try:
                import pyperclip
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            except:
                pyautogui.write(text, interval=0.005)

        def delete_chars(self, count):
            if count > 0:
                pyautogui.press('backspace', presses=count, interval=0.003)

        def process_audio(self):
            while self.is_running:
                if not self.is_listening:
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
                            result = json.loads(self.recognizer.Result())
                            text = result.get('text', '').strip()

                            if text:
                                self.delete_chars(self.chars_written)
                                self.write_fast(text + ' ')
                                self.chars_written = 0
                                self.last_partial = ""
                        else:
                            partial = json.loads(self.recognizer.PartialResult())
                            partial_text = partial.get('partial', '').strip()

                            if partial_text and partial_text != self.last_partial:
                                self.delete_chars(self.chars_written)
                                self.write_fast(partial_text)
                                self.chars_written = len(partial_text)
                                self.last_partial = partial_text

                except queue.Empty:
                    continue
                except:
                    pass

        def toggle_listening(self):
            with self.lock:
                self.is_listening = not self.is_listening
                self.last_partial = ""
                self.chars_written = 0

                if self.is_listening:
                    self.reset_recognizer()
                    while not self.audio_queue.empty():
                        try:
                            self.audio_queue.get_nowait()
                        except:
                            break

            self.update_icon()
            freq = 800 if self.is_listening else 400
            threading.Thread(target=lambda: winsound.Beep(freq, 80), daemon=True).start()

        def update_icon(self):
            if self.icon:
                self.icon.icon = self.create_icon(self.is_listening)
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
            self.toggle_listening()

        def get_status_text(self, item):
            return "Desactivar (F9)" if self.is_listening else "Activar (F9)"

        def run(self):
            self.load_model()

            keyboard.on_press_key(TOGGLE_KEY, lambda _: self.toggle_listening(), suppress=False)

            threading.Thread(target=self.process_audio, daemon=True).start()

            self.stream = sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=2000,
                dtype='int16',
                channels=1,
                callback=self.audio_callback
            )
            self.stream.start()

            menu = pystray.Menu(
                pystray.MenuItem(self.get_status_text, self.toggle_from_menu, default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Salir", self.quit_app)
            )

            self.icon = pystray.Icon(
                name="VoxF9",
                icon=self.create_icon(False),
                title="VoxF9 - Inactivo",
                menu=menu
            )

            self.icon.run()

    app = VoxF9()
    app.run()

if __name__ == "__main__":
    main()
