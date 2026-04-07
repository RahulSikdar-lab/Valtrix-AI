<p align="center">
  <h1 align="center">✦ VALTRIX AI</h1>
  <p align="center"><strong>Intelligent Voice-Controlled Desktop Assistant</strong></p>
  <p align="center">
    AES-256-GCM Encrypted Vault &nbsp;•&nbsp; 100+ App Launcher &nbsp;•&nbsp; Real-Time System Monitor &nbsp;•&nbsp; 5 Premium Themes
  </p>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Voice Commands](#voice-commands)
- [Secure Vault — AES-256-GCM](#secure-vault--aes-256-gcm)
- [Themes](#themes)
- [System Tray](#system-tray)
- [Usage Analytics](#usage-analytics)
- [File Reference](#file-reference)
- [Dependencies](#dependencies)
- [Security Details](#security-details)
- [Troubleshooting](#troubleshooting)
- [Future Roadmap](#future-roadmap)
- [License](#license)

---

## Overview

**Valtrix AI** is a professional-grade, voice-controlled desktop assistant for Windows. It combines voice recognition, application management, web search, encrypted file storage, and real-time system monitoring — all wrapped in a modern, themeable dark-mode GUI.

| Metric               | Value                  |
|-----------------------|------------------------|
| Python Version        | 3.10+                  |
| Platform              | Windows (SAPI5 TTS)    |
| Total Source Lines     | ~2,000                 |
| Encryption Standard   | AES-256-GCM (AWS-grade)|
| GUI Framework         | CustomTkinter          |
| Supported Apps        | 100+                   |
| Color Themes          | 5                      |

---

## Features

### 🎤 Voice Recognition
- Google Speech API with English-India (`en-in`) language model
- Enhanced noise reduction with ambient calibration (2-second warm-up)
- Dynamic energy threshold that adapts to environment
- Configurable pause threshold (0.8s) and listen timeout (6s)
- Visual waveform feedback showing idle / listening / speaking states

### 🖥️ Real-Time System Monitor
- **CPU Usage** — Live percentage with animated progress bar
- **RAM Usage** — Used/Total GB with percentage bar
- **Disk Usage** — Used/Total GB with percentage bar
- **System Info** — OS version, uptime counter
- Updates every 2 seconds via `psutil`

### 🚀 Application Launcher (100+ Apps)
Control any application with voice commands. Categories include:

| Category         | Examples                                    |
|------------------|---------------------------------------------|
| System Tools     | Task Manager, Control Panel, Registry Editor |
| Microsoft Office | Word, Excel, PowerPoint, Outlook, Teams     |
| Browsers         | Chrome, Edge, Firefox, Opera, Brave         |
| Dev Tools        | VS Code, PyCharm, IntelliJ, Android Studio  |
| Media Players    | VLC, Spotify, iTunes, Audacity              |
| Communication    | Zoom, Discord, Slack, Telegram, WhatsApp    |
| Cloud Storage    | OneDrive, Google Drive, Dropbox             |
| Design           | Photoshop, Illustrator, Premiere Pro        |
| Gaming           | Steam, Epic Games, Valorant, Minecraft      |
| Utilities        | 7-Zip, WinRAR, OBS Studio, TeamViewer      |

Also supports opening any website by saying "open [domain.com]".

### 🔍 Web Search
- **Google Search** — "Google [query]" opens browser + reads Wikipedia summary
- **YouTube Search** — "YouTube [query]" opens YouTube results + auto-plays
- **Wikipedia** — "What is [topic]" reads a 2-sentence summary aloud

### 🔒 Secure Vault (AES-256-GCM)
- AWS-standard AES-256-GCM encryption for all stored files
- PBKDF2-HMAC-SHA256 key derivation (600,000 iterations)
- Each file encrypted individually inside the app directory
- Password-protected with GCM authentication verification
- Intruder detection: captures webcam photo + screenshot on failed login
- Upload, download, open, and delete encrypted files through modern GUI

### 🔊 Media & Volume Control
- **Pause/Play** — Press K key (YouTube/VLC shortcut)
- **Mute** — Press M key
- **Volume Up/Down** — Simulates media key presses via `pynput`

### 🎨 5 Premium Themes
Instantly switch between color schemes from the header dropdown:
- **Midnight** — Deep blue-black with blue accents (default)
- **Cyberpunk** — Neon magenta & green on dark purple
- **Ocean** — Navy blue with teal/cyan accents
- **Emerald** — Dark forest green with emerald highlights
- **Rose** — Dark wine with pink/red accents

### 💬 Chat Bubble Interface
- User messages: right-aligned blue bubbles with timestamps
- Valtrix responses: left-aligned dark bubbles with accent headers
- System messages: centered in dim text
- Thread-safe message queue prevents GUI crashes

### 🌊 Animated Waveform Visualizer
- **Idle** — Subtle pulsing dark bars
- **Listening** — Energetic green-to-blue gradient with random amplitudes
- **Speaking** — Smooth purple sine wave pattern

### 🔽 System Tray
- Minimize to system tray via the "Tray" button
- Right-click tray icon: Show / Quit
- Double-click: restore window
- Falls back to regular minimize if `pystray` unavailable

### 📊 Usage Analytics
- Tracks total commands, today's commands, session count
- Command type breakdown with visual bar chart
- Daily command count shown in status bar
- Data persisted in `analytics.json`

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ TTS      │  │ Voice    │  │ System           │  │
│  │ Engine   │  │ Recog.   │  │ Monitor (psutil) │  │
│  │ (pyttsx3)│  │ (sr)     │  │                  │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       │              │                 │            │
│       ▼              ▼                 ▼            │
│  ┌─────────────────────────────────────────────┐    │
│  │              gui.py (CustomTkinter)         │    │
│  │  ┌────────┐ ┌──────────┐ ┌───────────────┐ │    │
│  │  │Waveform│ │Chat      │ │Theme Switcher │ │    │
│  │  │Canvas  │ │Bubbles   │ │(5 themes)     │ │    │
│  │  └────────┘ └──────────┘ └───────────────┘ │    │
│  │  ┌────────────────┐ ┌──────────────────┐   │    │
│  │  │System Monitor  │ │Usage Analytics   │   │    │
│  │  │Cards (4x)      │ │Dashboard         │   │    │
│  │  └────────────────┘ └──────────────────┘   │    │
│  └─────────────────────────────────────────────┘    │
│       │              │                 │            │
│       ▼              ▼                 ▼            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │openapp.py│  │SearchNow │  │secure_vault.py   │  │
│  │100+ apps │  │Google/YT │  │AES-256-GCM       │  │
│  │          │  │Wikipedia │  │Intruder Detection │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                       │             │
│  ┌──────────────┐  ┌──────────────────▼──────────┐  │
│  │greeting.py   │  │secure_vault/ (app dir)      │  │
│  │keyboardfn.py │  │  vault.salt / vault.verify  │  │
│  └──────────────┘  │  vault_meta.enc             │  │
│                    │  files/ *.enc                │  │
│                    │  intruders/ cam_*.jpg        │  │
│                    └─────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Data Flow

```
Voice Input ──► Microphone ──► SpeechRecognition ──► Google API
                                                        │
                                                        ▼
                                                   Query String
                                                        │
                              ┌──────────────────────────┼───────────────┐
                              ▼                          ▼               ▼
                         openapp.py               SearchNow.py    secure_vault.py
                         (open/close)             (google/yt/wiki)  (vault cmds)
                              │                          │               │
                              ▼                          ▼               ▼
                         os.system()              webbrowser       AES-256-GCM
                         taskkill                 pywhatkit        encrypt/decrypt
```

---

## Installation

### Prerequisites
- **Python 3.10+** (tested on 3.13)
- **Windows 10/11** (SAPI5 text-to-speech required)
- **Microphone** for voice input
- **Webcam** (optional, for intruder detection)

### Steps

```bash
# 1. Clone or download the project
cd Desktop-Assistant-pro

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Launch
python main.py
```

### Dependencies (13 packages)

| Package            | Version | Purpose                        |
|--------------------|---------|--------------------------------|
| `pyttsx3`          | latest  | Text-to-speech (SAPI5)         |
| `SpeechRecognition`| latest  | Voice input via Google API     |
| `pyautogui`        | latest  | Keyboard simulation, screenshots|
| `wikipedia`        | latest  | Wikipedia summaries            |
| `pywhatkit`        | latest  | Google/YouTube search          |
| `pynput`           | latest  | Volume control keys            |
| `bcrypt`           | latest  | Password hashing (legacy)      |
| `cryptography`     | latest  | AES-256-GCM encryption         |
| `opencv-python`    | latest  | Webcam capture (intruder)      |
| `Pillow`           | latest  | Image processing               |
| `psutil`           | latest  | System monitoring              |
| `customtkinter`    | latest  | Modern GUI framework           |
| `pystray`          | latest  | System tray integration        |

---

## Usage Guide

### Launching the App
```bash
python main.py
```
The GUI opens with:
- **Sidebar** (left): Home, Vault, Help, Stats navigation
- **System Cards** (top): Live CPU, RAM, Disk, Uptime
- **Chat Area** (center): Conversation log with bubbles + waveform
- **Controls** (bottom): Start Listening, Vault, Exit, Help, Stats, Tray

### Starting Voice Control
1. Click **🎤 Start Listening**
2. Wait for "Valtrix AI is now online" greeting
3. Speak commands naturally
4. Watch the waveform animate as you speak

### Stopping
- Say **"sleep mode"** — pauses the assistant loop
- Say **"deactivate"** — shuts down entirely
- Click **⏻ Exit** — closes the window

---

## Voice Commands

| Command                  | Action                              | Category       |
|--------------------------|-------------------------------------|----------------|
| `hello`                  | Greets you back                     | Greeting       |
| `open chrome`            | Launches Google Chrome              | App Control    |
| `open notepad`           | Launches Notepad                    | App Control    |
| `open spotify`           | Launches Spotify                    | App Control    |
| `open facebook.com`      | Opens website in browser            | Web            |
| `close chrome`           | Kills Chrome process                | App Control    |
| `close 3 tab`            | Closes 3 browser tabs (Ctrl+W)     | App Control    |
| `google machine learning`| Searches Google + reads summary    | Search         |
| `youtube lofi music`     | Searches & plays on YouTube        | Search         |
| `what is python`         | Reads Wikipedia summary             | Knowledge      |
| `who is Elon Musk`       | Wikipedia lookup                    | Knowledge      |
| `volume up`              | Increases volume (5 steps)          | Media          |
| `volume down`            | Decreases volume (5 steps)          | Media          |
| `pause`                  | Pauses video (K key)                | Media          |
| `play`                   | Plays video (K key)                 | Media          |
| `mute`                   | Mutes video (M key)                 | Media          |
| `sleep mode`             | Pauses voice loop                   | System         |
| `deactivate`             | Shuts down Valtrix AI               | System         |

---

## Secure Vault — AES-256-GCM

### Encryption Specification

| Parameter             | Value                                     |
|-----------------------|-------------------------------------------|
| **Algorithm**         | AES-256-GCM (Galois/Counter Mode)         |
| **Key Size**          | 256 bits (32 bytes)                       |
| **Nonce Size**        | 96 bits (12 bytes) — GCM standard         |
| **Salt Size**         | 128 bits (16 bytes)                       |
| **Auth Tag**          | 128 bits (16 bytes) — built into GCM      |
| **Key Derivation**    | PBKDF2-HMAC-SHA256                        |
| **KDF Iterations**    | 600,000 (OWASP 2023 recommendation)       |
| **Nonce Generation**  | `os.urandom()` — cryptographically secure  |

This is the **same encryption standard used by AWS KMS** (Key Management Service).

### How It Works

```
┌──────────────────────────────────────────────────┐
│                  SETUP (First Time)              │
│                                                  │
│  User Password ──► PBKDF2(password, salt) ──► Key│
│                         │                        │
│                         ▼                        │
│  AES-256-GCM.encrypt("VALTRIX_VAULT_VALID", Key)│
│                         │                        │
│                         ▼                        │
│  Save: vault.salt + vault.verify                 │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│                  UNLOCK (Login)                  │
│                                                  │
│  Entered Password + Stored Salt ──► PBKDF2 ──► Key
│                                        │         │
│  Decrypt vault.verify with Key         │         │
│  If plaintext == "VALTRIX_VAULT_VALID" │         │
│     ──► Password correct, load metadata│         │
│  Else                                  │         │
│     ──► WRONG PASSWORD ──► Log intruder│         │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│                FILE ENCRYPTION                   │
│                                                  │
│  Upload: file_bytes ──► AES-256-GCM(Key) ──►     │
│          nonce(12) + ciphertext + tag(16)         │
│          Saved as: files/<uuid>.enc              │
│                                                  │
│  Download: Read .enc ──► AES-256-GCM.decrypt ──► │
│            original file bytes                   │
└──────────────────────────────────────────────────┘
```

### Directory Structure

```
secure_vault/                  (hidden folder inside app directory)
├── vault.salt                 (16 bytes — random salt, hidden)
├── vault.verify               (encrypted verification token, hidden)
├── vault_meta.enc             (encrypted JSON — file index)
├── intruder_logs.json         (intrusion attempt records)
├── files/
│   ├── a1b2c3d4-...-.enc     (individually encrypted files)
│   ├── e5f6g7h8-...-.enc
│   └── ...
└── intruders/
    ├── cam_2026-04-07_20-30-15.jpg   (webcam captures)
    ├── ss_2026-04-07_20-30-15.png    (screenshots)
    └── ...
```

### Intruder Detection

When a wrong password is entered:
1. **Webcam Photo** — Captures a photo using OpenCV (2-second delay for camera init)
2. **Screenshot** — Captures current screen using PyAutoGUI
3. **Timestamp Log** — Records attempt time in `intruder_logs.json`
4. **Voice Alert** — Speaks "Unauthorized access attempt recorded"

View intruder logs from the Vault GUI → "🚨 Intruder Logs" button.

---

## Themes

### Available Themes

| Theme       | Background | Accent    | Feel                    |
|-------------|------------|-----------|-------------------------|
| **Midnight**| `#0b0f19`  | `#3b82f6` | Deep blue-black, professional |
| **Cyberpunk**| `#0a0a0f` | `#ff00ff` | Neon magenta, futuristic |
| **Ocean**   | `#0a192f`  | `#64ffda` | Navy with teal, calm     |
| **Emerald** | `#0a1a14`  | `#10b981` | Forest green, nature     |
| **Rose**    | `#1a0a14`  | `#f43f5e` | Wine red, elegant        |

### Switching Themes
1. Click the **theme dropdown** in the top-right header
2. Select a theme name
3. The GUI instantly rebuilds with the new colors
4. Your preference is saved to `valtrix_config.json`

### Theme Color Properties (14 keys per theme)
```
bg, card, sidebar, accent, green, red, yellow, purple,
text, dim, border, chat_bg, user_bubble, bot_bubble
```

---

## System Tray

1. Click the **🔽 Tray** button in the control bar
2. The window hides and a blue tray icon appears in the system tray
3. **Right-click** the tray icon → "Show Valtrix AI" or "Quit"
4. **Double-click** → brings the window back

> **Note**: Requires `pystray` package. If not installed, clicking Tray will minimize to taskbar instead.

---

## Usage Analytics

Access via the **📊 Stats** button or sidebar icon.

### Tracked Metrics
| Metric            | Description                         |
|-------------------|-------------------------------------|
| Total Commands    | Lifetime command count              |
| Today's Commands  | Commands since midnight             |
| Sessions          | Number of app launches              |
| Command Types     | Breakdown by category with bar chart |

### Command Categories Tracked
`greeting`, `media_control`, `volume`, `open_app`, `close_app`,
`google_search`, `youtube_search`, `wikipedia`, `sleep_mode`, `deactivate`

### Data Storage
Analytics are saved to `analytics.json` in the app directory:
```json
{
  "total": 42,
  "today": 7,
  "today_date": "2026-04-07",
  "types": {
    "open_app": 15,
    "google_search": 8,
    "greeting": 6
  },
  "daily": {
    "2026-04-07": 7,
    "2026-04-06": 12
  },
  "sessions": 5
}
```

---

## File Reference

### Source Files

| File | Lines | Size | Description |
|------|-------|------|-------------|
| [main.py](main.py) | 302 | 9.6 KB | Entry point — TTS, voice loop, system monitor, analytics |
| [gui.py](gui.py) | 542 | 24.3 KB | GUI — themes, waveform, chat bubbles, analytics popup |
| [secure_vault.py](secure_vault.py) | 588 | 24.4 KB | AES-256-GCM vault, intruder detection, vault GUI |
| [openapp.py](openapp.py) | 180 | 5.3 KB | 100+ app mappings, open/close by voice |
| [SearchNow.py](SearchNow.py) | 52 | 1.6 KB | Google, YouTube, Wikipedia search |
| [greeting.py](greeting.py) | 14 | 335 B | Time-based greeting (morning/afternoon/evening) |
| [keyboardfunction.py](keyboardfunction.py) | 16 | 410 B | Volume up/down via pynput |
| [requirements.txt](requirements.txt) | 13 | 133 B | Python package dependencies |

### Generated Files (auto-created at runtime)

| File | Purpose |
|------|---------|
| `valtrix_config.json` | Theme preference |
| `analytics.json` | Usage statistics |
| `secure_vault/vault.salt` | Encryption salt (hidden) |
| `secure_vault/vault.verify` | Password verification token (hidden) |
| `secure_vault/vault_meta.enc` | Encrypted file index |
| `secure_vault/files/*.enc` | Encrypted user files |
| `secure_vault/intruders/*.jpg/.png` | Intruder evidence |
| `secure_vault/intruder_logs.json` | Intrusion attempt log |

### Key Classes

| Class | File | Purpose |
|-------|------|---------|
| `AES256GCMEngine` | secure_vault.py | Static encryption/decryption methods |
| `SecureVaultStorage` | secure_vault.py | Vault lifecycle: setup, unlock, file ops |
| `WaveformVisualizer` | gui.py | Canvas-based animated audio visualizer |
| `ChatDisplay` | gui.py | Thread-safe chat bubble interface |
| `UsageAnalytics` | gui.py | Command tracking & stats dashboard |
| `EnhancedVoiceRecognizer` | main.py | Noise-calibrated speech recognition |

---

## Security Details

### Encryption Chain
```
User Password
      │
      ▼
PBKDF2-HMAC-SHA256 (600,000 iterations + 16-byte random salt)
      │
      ▼
256-bit AES Key
      │
      ├──► Encrypt verification token (vault.verify)
      ├──► Encrypt file metadata (vault_meta.enc)
      └──► Encrypt each file individually (files/*.enc)
            │
            ▼
      Each encrypted file = nonce(12 bytes) + ciphertext + GCM tag(16 bytes)
```

### Why AES-256-GCM?
- **Same standard used by AWS KMS**, Google Cloud KMS, and Azure Key Vault
- **Authenticated encryption** — detects any tampering automatically
- **GCM mode** — counter-based (no padding oracle attacks unlike CBC)
- **256-bit keys** — quantum-resistant at current key sizes

### Security Best Practices Implemented
- ✅ Cryptographically secure random nonces (`os.urandom`)
- ✅ Unique nonce per encryption operation (never reused)
- ✅ PBKDF2 with 600K iterations (exceeds OWASP 2023 minimum)
- ✅ Vault directory hidden on Windows (`FILE_ATTRIBUTE_HIDDEN`)
- ✅ Session key cleared from memory on vault lock
- ✅ No password stored — only salt + encrypted verification token
- ✅ Intruder evidence captured on failed access

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `UnicodeEncodeError` in terminal | Terminal encoding issue — doesn't affect GUI. Run with `PYTHONIOENCODING=utf-8` |
| `No module named 'customtkinter'` | Run `pip install customtkinter` |
| Microphone not detected | Check mic permissions in Windows Settings → Privacy → Microphone |
| TTS engine error on startup | Ensure SAPI5 voices are installed (Windows default) |
| Camera error in vault | Webcam not required — vault works without it, just skips photo capture |
| Theme not persisting | Check write permissions in app directory for `valtrix_config.json` |
| Vault data from old version | Old Fernet-encrypted data is incompatible — re-upload files to new vault |

---

## Future Roadmap

- [ ] 🤖 **Gemini AI Integration** — Intelligent conversation via Google Gemini API
- [ ] 📋 **Clipboard Manager** — Encrypted clipboard history
- [ ] ⏰ **Reminders & Alarms** — Voice-triggered task scheduling
- [ ] 📧 **Email Integration** — Read/compose via Gmail API
- [ ] 🔑 **Password Manager** — Store credentials in AES-256 vault
- [ ] 👁️ **Face Unlock** — OpenCV face recognition for vault
- [ ] 📝 **Voice Notes** — Record and transcribe voice memos
- [ ] 🗓️ **Calendar Integration** — Google Calendar read/write
- [ ] ☁️ **Weather Updates** — Real-time weather via API
- [ ] 📱 **Android APK** — Mobile companion app

---

## License

This project is for personal and educational use.

---

<p align="center">
  <strong>Built with ❤️ by Rahul Sikdar</strong><br>
  <em>Valtrix AI — Your Intelligent Desktop Companion</em>
</p>
