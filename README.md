<p align="center">
  <img src="icon.webp" alt="VoxF9 Logo" width="150"/>
</p>

<h1 align="center">VoxF9</h1>

<p align="center">
  <strong>Voz a texto en tiempo real con un solo botón</strong>
</p>

<p align="center">
  <a href="#características">Características</a> •
  <a href="#instalación">Instalación</a> •
  <a href="#uso">Uso</a> •
  <a href="#tecnologías">Tecnologías</a> •
  <a href="#contribuir">Contribuir</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
  <img src="https://img.shields.io/badge/Vosk-Offline-FF6F00?style=for-the-badge" alt="Vosk"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"/>
</p>

---

## 🎙️ ¿Qué es VoxF9?

**VoxF9** es una aplicación de escritorio para Windows que transcribe tu voz a texto en tiempo real. Funciona completamente offline, sin necesidad de internet ni suscripciones.

¿Cansado de escribir? Con VoxF9 solo necesitas:

- 🎤 **Presionar F9** = Activar/Desactivar
- 🗣️ **Hablar** = El texto aparece donde esté tu cursor

¡Así de fácil! Funciona en cualquier aplicación: navegador, Word, chat, IDE, etc.

---

## ✨ Características

### ⚡ Transcripción en Tiempo Real
- Escribe mientras hablas
- Resultados parciales que se actualizan al instante
- Latencia mínima

### 🔒 100% Offline y Privado
- No requiere internet
- Tu voz nunca sale de tu computadora
- Sin suscripciones ni costos ocultos

### 🎯 Súper Simple
- Un solo botón: **F9**
- Sin ventanas molestas
- Corre en segundo plano (system tray)

### 🌐 Funciona en Cualquier App
- Navegadores
- Microsoft Office
- IDEs (VS Code, etc.)
- Chats (Discord, Slack, etc.)
- Cualquier lugar donde puedas escribir

### 🇪🇸 Optimizado para Español
- Modelo de voz en español incluido
- Alta precisión con acentos latinoamericanos

---

## 🚀 Instalación

### Opción 1: Ejecutable (Recomendado)

1. Descarga `VoxF9.exe` desde [Releases](https://github.com/Avzolem/voxf9/releases)
2. Ejecuta el archivo
3. La primera vez descargará el modelo de voz (~1.4 GB)
4. ¡Listo! Presiona **F9** para empezar

### Opción 2: Desde el Código Fuente

#### Requisitos
- Python 3.12+
- Windows 10/11

#### Instalación

```bash
# Clonar repositorio
git clone https://github.com/Avzolem/voxf9.git
cd voxf9

# Instalar dependencias
pip install vosk sounddevice pyautogui keyboard pystray pillow pyperclip

# Ejecutar
python voxf9.pyw
```

---

## 📖 Uso

### Iniciar VoxF9
- Doble clic en `VoxF9.exe` o el acceso directo
- Aparecerá un ícono en el **system tray** (barra de tareas)

### Dictar Texto
1. Haz clic donde quieras escribir
2. Presiona **F9** (escucharás un beep agudo)
3. Habla normalmente
4. El texto aparece en tiempo real
5. Presiona **F9** de nuevo para pausar (beep grave)

### Menú del System Tray
- **Clic derecho** en el ícono:
  - Activar/Desactivar (F9)
  - Salir

### Cerrar VoxF9
- Clic derecho en el ícono → **Salir**
- O ejecutar `Desinstalar.bat` para eliminar completamente

---

## 🛠️ Tecnologías

| Tecnología | Uso |
|------------|-----|
| **Python** | Lenguaje principal |
| **Vosk** | Motor de reconocimiento de voz offline |
| **sounddevice** | Captura de audio |
| **pyautogui** | Simulación de escritura |
| **pystray** | Ícono en system tray |
| **keyboard** | Hotkey global (F9) |

---

## 📁 Estructura del Proyecto

```
voxf9/
├── voxf9.pyw          # Aplicación principal
├── VoxF9.vbs          # Iniciador silencioso
├── VoxF9.exe          # Ejecutable compilado
├── Desinstalar.bat    # Desinstalador
├── icon.ico           # Ícono de la app
├── icon.webp          # Logo para README
└── README.md          # Este archivo
```

---

## 🗑️ Desinstalación

1. Ejecuta `Desinstalar.bat`
2. Confirma con "S"
3. Se eliminarán:
   - El ejecutable
   - El modelo de voz (1.4 GB)
   - El acceso directo del escritorio

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si quieres mejorar VoxF9:

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/NuevaFuncion`)
3. Haz commit de tus cambios (`git commit -m 'Agregar nueva función'`)
4. Push a la rama (`git push origin feature/NuevaFuncion`)
5. Abre un Pull Request

### Ideas para Contribuir
- [ ] Soporte para más idiomas
- [ ] Hotkey configurable
- [ ] Comandos de voz (puntuación, nueva línea, etc.)
- [ ] Integración con GPU/NPU para mayor velocidad
- [ ] Versión para macOS/Linux

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autor

<p align="center">
  <strong>Desarrollado con ❤️ por <a href="https://avsolem.com">avsolem.com</a></strong>
</p>

---

<p align="center">
  <sub>¿Te gusta VoxF9? ¡Dale una ⭐ al repo!</sub>
</p>
