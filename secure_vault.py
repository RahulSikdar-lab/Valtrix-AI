import os
import sys
import json
import uuid
import time
import datetime
import tempfile
import subprocess
import base64
import io
import hashlib

import cv2
import pyautogui
from PIL import Image
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# ══════════════════════════════════════════════════════════════
#  AES-256-GCM ENCRYPTION ENGINE  (AWS-Standard Algorithm)
# ══════════════════════════════════════════════════════════════

class AES256GCMEngine:
    """
    AWS-standard AES-256-GCM encryption engine.
    Uses PBKDF2-HMAC-SHA256 for key derivation with 600,000 iterations.
    Each encryption generates a unique 12-byte nonce for GCM.
    """
    SALT_SIZE = 16          # 128-bit salt
    NONCE_SIZE = 12         # 96-bit nonce (GCM standard)
    KEY_SIZE = 32           # 256-bit key
    ITERATIONS = 600_000    # OWASP 2023 recommendation for PBKDF2-SHA256

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=AES256GCMEngine.KEY_SIZE,
            salt=salt,
            iterations=AES256GCMEngine.ITERATIONS,
        )
        return kdf.derive(password.encode('utf-8'))

    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> bytes:
        nonce = os.urandom(AES256GCMEngine.NONCE_SIZE)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    @staticmethod
    def decrypt(data: bytes, key: bytes) -> bytes:
        nonce = data[:AES256GCMEngine.NONCE_SIZE]
        ciphertext = data[AES256GCMEngine.NONCE_SIZE:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)


# ══════════════════════════════════════════════════════════════
#  SECURE VAULT STORAGE
# ══════════════════════════════════════════════════════════════

class SecureVaultStorage:
    """Encrypted file vault with AES-256-GCM. Files stored inside the app directory."""

    VERIFY_TOKEN = b"VALTRIX_VAULT_AES256GCM_VALID"

    def __init__(self):
        self.vault_dir = self._get_vault_directory()
        self.files_dir = os.path.join(self.vault_dir, "files")
        self.intruder_dir = os.path.join(self.vault_dir, "intruders")
        self.salt_file = os.path.join(self.vault_dir, "vault.salt")
        self.verify_file = os.path.join(self.vault_dir, "vault.verify")
        self.meta_file = os.path.join(self.vault_dir, "vault_meta.enc")
        self.intruder_log_file = os.path.join(self.vault_dir, "intruder_logs.json")

        os.makedirs(self.files_dir, exist_ok=True)
        os.makedirs(self.intruder_dir, exist_ok=True)

        self._session_key = None
        self._metadata = {"files": {}}

    def _get_vault_directory(self):
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        vault_dir = os.path.join(app_dir, "secure_vault")
        os.makedirs(vault_dir, exist_ok=True)
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(vault_dir, 0x02)
            except Exception:
                pass
        return vault_dir

    def is_setup(self) -> bool:
        return os.path.exists(self.salt_file) and os.path.exists(self.verify_file)

    def is_unlocked(self) -> bool:
        return self._session_key is not None

    # ── Setup & Auth ──────────────────────────────────────

    def setup(self, password: str) -> bool:
        try:
            salt = os.urandom(AES256GCMEngine.SALT_SIZE)
            key = AES256GCMEngine.derive_key(password, salt)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            encrypted_verify = AES256GCMEngine.encrypt(self.VERIFY_TOKEN, key)
            with open(self.verify_file, 'wb') as f:
                f.write(encrypted_verify)
            self._session_key = key
            self._metadata = {"files": {}}
            self._save_metadata()
            self._hide_file(self.salt_file)
            self._hide_file(self.verify_file)
            return True
        except Exception as e:
            print(f"Vault setup error: {e}")
            return False

    def unlock(self, password: str) -> bool:
        try:
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
            key = AES256GCMEngine.derive_key(password, salt)
            with open(self.verify_file, 'rb') as f:
                encrypted_verify = f.read()
            plaintext = AES256GCMEngine.decrypt(encrypted_verify, key)
            if plaintext == self.VERIFY_TOKEN:
                self._session_key = key
                self._load_metadata()
                return True
            return False
        except Exception:
            return False

    def lock(self):
        self._session_key = None
        self._metadata = {"files": {}}

    # ── File Operations ───────────────────────────────────

    def upload_file(self, filepath: str) -> bool:
        if not self._session_key:
            return False
        try:
            with open(filepath, 'rb') as f:
                file_data = f.read()
            file_id = str(uuid.uuid4())
            encrypted = AES256GCMEngine.encrypt(file_data, self._session_key)
            enc_path = os.path.join(self.files_dir, f"{file_id}.enc")
            with open(enc_path, 'wb') as f:
                f.write(encrypted)
            self._metadata["files"][file_id] = {
                "name": os.path.basename(filepath),
                "size": len(file_data),
                "uploaded": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            self._save_metadata()
            return True
        except Exception as e:
            print(f"Upload error: {e}")
            return False

    def download_file(self, file_id: str, dest_dir: str):
        if not self._session_key:
            return None
        try:
            enc_path = os.path.join(self.files_dir, f"{file_id}.enc")
            with open(enc_path, 'rb') as f:
                encrypted = f.read()
            file_data = AES256GCMEngine.decrypt(encrypted, self._session_key)
            filename = self._metadata["files"][file_id]["name"]
            dest_path = os.path.join(dest_dir, filename)
            with open(dest_path, 'wb') as f:
                f.write(file_data)
            return dest_path
        except Exception as e:
            print(f"Download error: {e}")
            return None

    def open_file_temp(self, file_id: str):
        if not self._session_key:
            return None
        try:
            enc_path = os.path.join(self.files_dir, f"{file_id}.enc")
            with open(enc_path, 'rb') as f:
                encrypted = f.read()
            file_data = AES256GCMEngine.decrypt(encrypted, self._session_key)
            filename = self._metadata["files"][file_id]["name"]
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            with open(temp_path, 'wb') as f:
                f.write(file_data)
            if sys.platform.startswith('win'):
                os.startfile(temp_path)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', temp_path])
            else:
                subprocess.Popen(['xdg-open', temp_path])
            return temp_path
        except Exception as e:
            print(f"Open error: {e}")
            return None

    def delete_file(self, file_id: str) -> bool:
        if not self._session_key:
            return False
        try:
            enc_path = os.path.join(self.files_dir, f"{file_id}.enc")
            if os.path.exists(enc_path):
                os.remove(enc_path)
            if file_id in self._metadata["files"]:
                del self._metadata["files"][file_id]
            self._save_metadata()
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    def list_files(self) -> dict:
        return self._metadata.get("files", {})

    # ── Metadata ──────────────────────────────────────────

    def _save_metadata(self):
        if not self._session_key:
            return
        meta_json = json.dumps(self._metadata).encode('utf-8')
        encrypted = AES256GCMEngine.encrypt(meta_json, self._session_key)
        with open(self.meta_file, 'wb') as f:
            f.write(encrypted)

    def _load_metadata(self):
        if not self._session_key or not os.path.exists(self.meta_file):
            self._metadata = {"files": {}}
            return
        try:
            with open(self.meta_file, 'rb') as f:
                encrypted = f.read()
            meta_json = AES256GCMEngine.decrypt(encrypted, self._session_key)
            self._metadata = json.loads(meta_json.decode('utf-8'))
        except Exception:
            self._metadata = {"files": {}}

    # ── Intruder Detection ────────────────────────────────

    def log_intruder(self, speak_func=None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        entry = {"timestamp": timestamp, "camera": False, "screenshot": False}

        cam = None
        try:
            cam = cv2.VideoCapture(0)
            if cam.isOpened():
                time.sleep(2)
                ret, frame = cam.read()
                if ret and frame is not None:
                    photo_path = os.path.join(self.intruder_dir, f"cam_{timestamp}.jpg")
                    cv2.imwrite(photo_path, frame)
                    entry["camera"] = True
                    entry["photo"] = photo_path
        except Exception as e:
            print(f"Camera error: {e}")
        finally:
            if cam:
                cam.release()

        try:
            ss = pyautogui.screenshot()
            ss_path = os.path.join(self.intruder_dir, f"ss_{timestamp}.png")
            ss.save(ss_path)
            entry["screenshot"] = True
            entry["screenshot_path"] = ss_path
        except Exception as e:
            print(f"Screenshot error: {e}")

        logs = self.get_intruder_logs()
        logs.append(entry)
        with open(self.intruder_log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        if speak_func:
            speak_func("Unauthorized access attempt recorded.")

    def get_intruder_logs(self) -> list:
        if os.path.exists(self.intruder_log_file):
            try:
                with open(self.intruder_log_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    # ── Helpers ───────────────────────────────────────────

    @staticmethod
    def _hide_file(path):
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(path, 0x02)
            except Exception:
                pass

    @staticmethod
    def format_size(size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.1f} MB"
        return f"{size_bytes / (1024 ** 3):.2f} GB"


# ══════════════════════════════════════════════════════════════
#  GLOBAL VAULT INSTANCE
# ══════════════════════════════════════════════════════════════

vault_storage = SecureVaultStorage()


# ══════════════════════════════════════════════════════════════
#  PASSWORD DIALOG (customtkinter)
# ══════════════════════════════════════════════════════════════

def _ask_password(title="Vault Access", prompt="Enter your vault password:"):
    import customtkinter as ctk
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("420x220")
    dialog.configure(fg_color="#0b0f19")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.attributes("-topmost", True)
    result = [None]

    ctk.CTkLabel(dialog, text=prompt, font=("Arial", 14, "bold"),
                 text_color="#e2e8f0").pack(pady=(25, 10))

    entry = ctk.CTkEntry(dialog, show="•", width=280, height=40,
                         font=("Arial", 14), fg_color="#111827",
                         border_color="#3b82f6", text_color="#e2e8f0")
    entry.pack(pady=10)
    entry.focus_set()

    def submit():
        result[0] = entry.get()
        dialog.destroy()

    def cancel():
        dialog.destroy()

    bf = ctk.CTkFrame(dialog, fg_color="transparent")
    bf.pack(pady=15)
    ctk.CTkButton(bf, text="Unlock", command=submit, fg_color="#3b82f6",
                  hover_color="#2563eb", width=110, height=36,
                  font=("Arial", 12, "bold")).pack(side="left", padx=8)
    ctk.CTkButton(bf, text="Cancel", command=cancel, fg_color="#ef4444",
                  hover_color="#dc2626", width=110, height=36,
                  font=("Arial", 12, "bold")).pack(side="left", padx=8)
    entry.bind("<Return>", lambda e: submit())
    dialog.wait_window()
    return result[0]


# ══════════════════════════════════════════════════════════════
#  VAULT GUI
# ══════════════════════════════════════════════════════════════

def open_vault_gui():
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    import tkinter as tk

    BG = "#0b0f19"
    CARD = "#111827"
    BORDER = "#1e293b"
    TEXT = "#e2e8f0"
    DIM = "#64748b"
    ACCENT = "#3b82f6"

    vault_win = ctk.CTkToplevel()
    vault_win.title("🔒 Valtrix AI — Secure Vault (AES-256-GCM)")
    vault_win.geometry("900x580")
    vault_win.configure(fg_color=BG)
    vault_win.attributes("-topmost", True)
    vault_win.after(100, lambda: vault_win.attributes("-topmost", False))

    # Header
    header = ctk.CTkFrame(vault_win, fg_color="transparent", height=50)
    header.pack(fill="x", padx=20, pady=(15, 5))
    header.pack_propagate(False)
    ctk.CTkLabel(header, text="🔒  Secure Vault", font=("Arial", 20, "bold"),
                 text_color=TEXT).pack(side="left")
    ctk.CTkLabel(header, text="AES-256-GCM Encrypted Storage",
                 font=("Arial", 11), text_color=DIM).pack(side="left", padx=(12, 0), pady=(4, 0))

    # File list
    list_frame = ctk.CTkFrame(vault_win, fg_color=CARD, corner_radius=15,
                              border_width=1, border_color=BORDER)
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    cols_header = ctk.CTkFrame(list_frame, fg_color="#0d1117", corner_radius=0, height=35)
    cols_header.pack(fill="x", padx=2, pady=(2, 0))
    cols_header.pack_propagate(False)
    ctk.CTkLabel(cols_header, text="    Filename", font=("Arial", 10, "bold"),
                 text_color=DIM, anchor="w").pack(side="left", padx=15)
    ctk.CTkLabel(cols_header, text="Size", font=("Arial", 10, "bold"),
                 text_color=DIM).pack(side="right", padx=(0, 140))
    ctk.CTkLabel(cols_header, text="Uploaded", font=("Arial", 10, "bold"),
                 text_color=DIM).pack(side="right", padx=(0, 30))

    listbox = tk.Listbox(list_frame, bg="#0d1117", fg=TEXT, font=("Consolas", 11),
                         selectbackground=ACCENT, selectforeground="white",
                         highlightthickness=0, bd=0, relief="flat",
                         selectmode="extended", activestyle="none")
    scrollbar = ctk.CTkScrollbar(list_frame, command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    listbox.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
    scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=(0, 10))

    file_id_map = {}

    def refresh_list():
        listbox.delete(0, tk.END)
        file_id_map.clear()
        files = vault_storage.list_files()
        for idx, (fid, meta) in enumerate(files.items()):
            size_str = vault_storage.format_size(meta.get("size", 0))
            date_str = meta.get("uploaded", "")
            display = f"  {meta['name']:<40s}  {size_str:<12s}  {date_str}"
            listbox.insert(tk.END, display)
            file_id_map[idx] = fid

    def upload_files():
        paths = filedialog.askopenfilenames(title="Select Files to Upload to Vault")
        if not paths:
            return
        count = 0
        for p in paths:
            if vault_storage.upload_file(p):
                count += 1
        messagebox.showinfo("Upload Complete", f"{count} file(s) encrypted and stored.")
        refresh_list()

    def download_selected():
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select files to download.")
            return
        dest = filedialog.askdirectory(title="Select Download Location")
        if not dest:
            return
        for i in sel:
            fid = file_id_map.get(i)
            if fid:
                vault_storage.download_file(fid, dest)
        messagebox.showinfo("Downloaded", f"Files decrypted and saved to:\n{dest}")

    def open_selected():
        sel = listbox.curselection()
        if not sel or len(sel) != 1:
            messagebox.showwarning("Selection", "Select exactly one file to open.")
            return
        fid = file_id_map.get(sel[0])
        if fid:
            vault_storage.open_file_temp(fid)

    def delete_selected():
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select files to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Permanently delete selected files?"):
            return
        for i in sorted(sel, reverse=True):
            fid = file_id_map.get(i)
            if fid:
                vault_storage.delete_file(fid)
        messagebox.showinfo("Deleted", "Files removed from vault.")
        refresh_list()

    def view_intruder_logs():
        logs = vault_storage.get_intruder_logs()
        if not logs:
            messagebox.showinfo("Intruder Logs", "No intrusion attempts recorded.")
            return
        log_win = ctk.CTkToplevel(vault_win)
        log_win.title("🚨 Intruder Detection Logs")
        log_win.geometry("700x500")
        log_win.configure(fg_color=BG)

        ctk.CTkLabel(log_win, text="🚨 Intruder Detection Logs",
                     font=("Arial", 18, "bold"), text_color="#ef4444").pack(pady=15)

        scroll = ctk.CTkScrollableFrame(log_win, fg_color=BG)
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        for i, log in enumerate(logs):
            card = ctk.CTkFrame(scroll, fg_color=CARD, corner_radius=12,
                                border_width=1, border_color="#ef4444")
            card.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(card, text=f"Attempt {i + 1}  —  {log['timestamp']}",
                         font=("Arial", 12, "bold"), text_color="#f59e0b").pack(anchor="w", padx=15, pady=(10, 3))
            ctk.CTkLabel(card, text=f"Camera: {'✅' if log.get('camera') else '❌'}   |   Screenshot: {'✅' if log.get('screenshot') else '❌'}",
                         font=("Arial", 11), text_color=DIM).pack(anchor="w", padx=15, pady=(0, 8))

            media_frame = ctk.CTkFrame(card, fg_color="transparent")
            media_frame.pack(anchor="w", padx=15, pady=(0, 10))

            if log.get("photo") and os.path.exists(log["photo"]):
                ctk.CTkButton(media_frame, text="📷 View Photo", width=130,
                              fg_color="#415a77", hover_color="#5a7aa7",
                              command=lambda p=log["photo"]: os.startfile(p) if sys.platform.startswith("win") else None
                              ).pack(side="left", padx=5)

            if log.get("screenshot_path") and os.path.exists(log["screenshot_path"]):
                ctk.CTkButton(media_frame, text="🖥️ View Screenshot", width=150,
                              fg_color="#415a77", hover_color="#5a7aa7",
                              command=lambda p=log["screenshot_path"]: os.startfile(p) if sys.platform.startswith("win") else None
                              ).pack(side="left", padx=5)

    # Buttons
    btn_frame = ctk.CTkFrame(vault_win, fg_color="transparent", height=55)
    btn_frame.pack(fill="x", padx=20, pady=(0, 15))
    btn_frame.pack_propagate(False)

    btn_inner = ctk.CTkFrame(btn_frame, fg_color="transparent")
    btn_inner.pack(expand=True)

    buttons = [
        ("📤 Upload", upload_files, "#10b981", "#059669"),
        ("📥 Download", download_selected, ACCENT, "#2563eb"),
        ("📂 Open", open_selected, "#8b5cf6", "#7c3aed"),
        ("🗑️ Delete", delete_selected, "#ef4444", "#dc2626"),
        ("🚨 Intruder Logs", view_intruder_logs, "#f59e0b", "#d97706"),
    ]
    for text, cmd, fg, hover in buttons:
        ctk.CTkButton(btn_inner, text=text, command=cmd, fg_color=fg,
                      hover_color=hover, width=130, height=38, corner_radius=10,
                      font=("Arial", 11, "bold"),
                      text_color="white" if fg != "#f59e0b" else "#0a0e1a"
                      ).pack(side="left", padx=5)

    refresh_list()


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════

def verify_password_and_open_vault(speak_func=None):
    if not vault_storage.is_setup():
        pw = _ask_password("Vault Setup", "Create a vault password:")
        if not pw:
            if speak_func:
                speak_func("Vault setup cancelled.")
            return
        if len(pw) < 4:
            from tkinter import messagebox
            messagebox.showwarning("Weak Password", "Use at least 4 characters.")
        if vault_storage.setup(pw):
            if speak_func:
                speak_func("Vault created with AES-256 encryption.")
            open_vault_gui()
        return

    pw = _ask_password()
    if not pw:
        if speak_func:
            speak_func("Password entry cancelled.")
        return

    if vault_storage.unlock(pw):
        if speak_func:
            speak_func("Password verified. Vault unlocked.")
        open_vault_gui()
    else:
        if speak_func:
            speak_func("Incorrect password. Access denied. Intruder logged.")
        vault_storage.log_intruder(speak_func)