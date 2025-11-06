import os
import cv2
import bcrypt
import json
import shutil
import tkinter as tk
from tkinter import (
    Tk, Button, Label, Frame, Listbox, Scrollbar,
    END, RIGHT, LEFT, Y, BOTH, messagebox, filedialog,
    simpledialog, scrolledtext
)
import pyautogui
import datetime
import subprocess
import sys
import time
import base64
import pickle
from PIL import Image
import io
import hashlib
from cryptography.fernet import Fernet
import secrets
import string
import tempfile

# === TRULY SECURE VAULT STORAGE ===
class SecureVaultStorage:
    def __init__(self):
        self.vault_data = {}
        self.config_data = {}
        self.intruder_logs = []
        self.encryption_key = None
        self.vault_dir = self.get_vault_directory()
        self.vault_file = os.path.join(self.vault_dir, "secure_vault.enc")
        self.key_file = os.path.join(self.vault_dir, ".vault_key")
        self.setup_encryption()
        self.load_existing_data()
    
    def get_vault_directory(self):
        """Get vault directory inside app folder"""
        # Get directory where this script is located
        if getattr(sys, 'frozen', False):
            # If running as compiled exe
            app_dir = os.path.dirname(sys.executable)
        else:
            # If running as script
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        vault_dir = os.path.join(app_dir, "secure_vault")
        os.makedirs(vault_dir, exist_ok=True)
        
        # Set hidden attribute on Windows
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(vault_dir, 0x02)  # FILE_ATTRIBUTE_HIDDEN
            except:
                pass
        return vault_dir
    
    def setup_encryption(self):
        """Setup encryption key - stored securely in app directory"""
        if os.path.exists(self.key_file):
            # Load existing key
            try:
                with open(self.key_file, 'rb') as f:
                    encrypted_key = f.read()
                
                # Derive key from master password (if set)
                if "password" in self.config_data:
                    master_key = self.derive_key_from_password(self.config_data["password"])
                    fernet = Fernet(master_key)
                    self.encryption_key = fernet.decrypt(encrypted_key)
                else:
                    # First time setup - use device-specific key
                    device_key = self.generate_device_key()
                    fernet = Fernet(device_key)
                    self.encryption_key = fernet.decrypt(encrypted_key)
                    
            except Exception as e:
                print(f"Key loading error: {e}")
                self.generate_new_keys()
        else:
            self.generate_new_keys()
    
    def generate_new_keys(self):
        """Generate new encryption keys"""
        # Generate random encryption key
        self.encryption_key = Fernet.generate_key()
        
        # Generate device-specific key for protecting the encryption key
        device_key = self.generate_device_key()
        
        # Encrypt the main key with device key
        fernet = Fernet(device_key)
        encrypted_main_key = fernet.encrypt(self.encryption_key)
        
        # Save encrypted main key
        with open(self.key_file, 'wb') as f:
            f.write(encrypted_main_key)
        
        # Set hidden attribute on Windows
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(self.key_file, 0x02)  # FILE_ATTRIBUTE_HIDDEN
            except:
                pass
    
    def generate_device_key(self):
        """Generate device-specific key based on system properties"""
        import platform
        system_info = f"{platform.node()}{platform.processor()}{os.name}"
        return base64.urlsafe_b64encode(hashlib.sha256(system_info.encode()).digest())
    
    def derive_key_from_password(self, password_hash):
        """Derive encryption key from password"""
        return base64.urlsafe_b64encode(hashlib.sha256(password_hash.encode()).digest())
    
    def encrypt_data(self, data):
        """Encrypt data using Fernet encryption"""
        fernet = Fernet(self.encryption_key)
        encrypted_data = fernet.encrypt(pickle.dumps(data))
        return encrypted_data
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data using Fernet encryption"""
        try:
            fernet = Fernet(self.encryption_key)
            decrypted_data = pickle.loads(fernet.decrypt(encrypted_data))
            return decrypted_data
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
    
    def load_existing_data(self):
        """Load encrypted vault data from app directory"""
        try:
            if os.path.exists(self.vault_file):
                with open(self.vault_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.decrypt_data(encrypted_data)
                if decrypted_data:
                    self.vault_data = decrypted_data.get('vault_data', {})
                    self.config_data = decrypted_data.get('config_data', {})
                    self.intruder_logs = decrypted_data.get('intruder_logs', [])
        except Exception as e:
            print(f"Vault loading error: {e}")
            # Start fresh if loading fails
            self.vault_data = {}
            self.config_data = {}
            self.intruder_logs = []
    
    def save_to_disk(self):
        """Save encrypted vault data to app directory"""
        try:
            data_to_save = {
                'vault_data': self.vault_data,
                'config_data': self.config_data,
                'intruder_logs': self.intruder_logs
            }
            
            encrypted_data = self.encrypt_data(data_to_save)
            
            with open(self.vault_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Set hidden attribute on Windows
            if os.name == 'nt':
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(self.vault_file, 0x02)  # FILE_ATTRIBUTE_HIDDEN
                except:
                    pass
                    
        except Exception as e:
            print(f"Failed to save vault: {e}")

# Create global vault storage
vault_storage = SecureVaultStorage()

def setup_vault(speak_func=None):
    if speak_func:
        speak_func("Setting up your secure vault for the first time.")
    password = simpledialog.askstring("Vault Setup", "Create a strong password:", show='*')
    if not password:
        if speak_func:
            speak_func("Password not set. Vault setup cancelled.")
        return False
    if len(password) < 4:
        messagebox.showwarning("Weak Password", "Consider using a stronger password (at least 4 characters).")
    
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    
    vault_storage.config_data["password"] = hashed.decode('utf-8')
    vault_storage.save_to_disk()
    
    if speak_func:
        speak_func("Vault setup completed successfully!")
    return True

def log_intruder(speak_func=None):
    """Log intruder attempts in memory"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    intruder_data = {
        "timestamp": timestamp,
        "camera_available": False,
        "screenshot_taken": False,
        "photo": None,
        "screenshot": None
    }
    
    # Try to take photo
    cam = None
    try:
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            # Allow camera to initialize
            time.sleep(2)
            ret, frame = cam.read()
            if ret and frame is not None:
                # Convert image to base64 for in-memory storage
                success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if success:
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    intruder_data["photo"] = img_base64
                    intruder_data["camera_available"] = True
                    print("Camera photo captured successfully")
    except Exception as e:
        print(f"Camera error: {e}")
    finally:
        if cam:
            cam.release()
    
    # Take screenshot
    try:
        screenshot = pyautogui.screenshot()
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Convert to base64
        screenshot_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
        intruder_data["screenshot"] = screenshot_base64
        intruder_data["screenshot_taken"] = True
        print("Screenshot captured successfully")
    except Exception as e:
        print(f"Screenshot error: {e}")
    
    # Add to intruder logs
    vault_storage.intruder_logs.append(intruder_data)
    vault_storage.save_to_disk()
    
    print(f"Intruder logged: Camera={intruder_data['camera_available']}, Screenshot={intruder_data['screenshot_taken']}")
    if speak_func:
        speak_func("Unauthorized access recorded and secured.")

def open_with_default(file_path):
    """Open a temporary file with default application"""
    try:
        if sys.platform.startswith('win'):
            os.startfile(file_path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', file_path])
        else:
            subprocess.Popen(['xdg-open', file_path])
    except Exception as e:
        messagebox.showerror("Open Error", f"Could not open: {e}")

def save_intruder_media(intruder_log, temp_dir):
    """Save intruder photos and screenshots to temporary files for viewing"""
    saved_files = []
    
    try:
        # Save photo if available
        if intruder_log.get('photo') and intruder_log.get('camera_available'):
            photo_data = base64.b64decode(intruder_log['photo'])
            photo_path = os.path.join(temp_dir, f"photo_{intruder_log['timestamp']}.jpg")
            with open(photo_path, 'wb') as f:
                f.write(photo_data)
            saved_files.append(("Camera Photo", photo_path))
        
        # Save screenshot if available
        if intruder_log.get('screenshot') and intruder_log.get('screenshot_taken'):
            screenshot_data = base64.b64decode(intruder_log['screenshot'])
            screenshot_path = os.path.join(temp_dir, f"screenshot_{intruder_log['timestamp']}.png")
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_data)
            saved_files.append(("Screenshot", screenshot_path))
            
    except Exception as e:
        print(f"Error saving intruder media: {e}")
    
    return saved_files

# === Vault GUI ===
def open_vault_gui():
    vault_win = Tk()
    vault_win.title("🔒 Secure Vault - Encrypted Storage")
    vault_win.geometry("800x520")
    vault_win.configure(bg="#0d1b2a")

    current_path = ["/"]  # Virtual path in memory storage

    Label(vault_win, text="Your Secure Vault (Encrypted Storage)", bg="#0d1b2a", fg="#e0e1dd", font=("Arial", 16, "bold")).pack(pady=8)

    frame = Frame(vault_win, bg="#0d1b2a")
    frame.pack(fill=BOTH, expand=True, padx=10, pady=4)

    scrollbar = Scrollbar(frame, bg="#415a77")
    scrollbar.pack(side=RIGHT, fill=Y)

    listbox = Listbox(frame, selectmode="extended", yscrollcommand=scrollbar.set, bg="#1b263b", fg="#e0e1dd",
                      font=("Arial", 11), highlightbackground="#415a77", selectbackground="#778da9")
    listbox.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.config(command=listbox.yview)

    def get_current_files():
        """Get files from current virtual path"""
        if current_path[0] == "/":
            return list(vault_storage.vault_data.keys())
        return []

    def refresh_list():
        listbox.delete(0, END)
        try:
            items = get_current_files()
            for item in items:
                listbox.insert(END, item)
            
            # Always show intruder logs option
            listbox.insert(END, "[Intruder Logs]")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not read vault: {e}")

    def upload_files():
        files = filedialog.askopenfilenames(title="Select Files to Upload")
        for file_path in files:
            try:
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    file_b64 = base64.b64encode(file_content).decode('utf-8')
                    
                filename = os.path.basename(file_path)
                vault_storage.vault_data[filename] = {
                    "content": file_b64,
                    "upload_time": datetime.datetime.now().isoformat(),
                    "size": len(file_content)
                }
            except Exception as e:
                messagebox.showerror("Upload Error", f"Could not upload {file_path}: {e}")
        
        vault_storage.save_to_disk()
        messagebox.showinfo("Success", "Files uploaded to secure vault.")
        refresh_list()

    def download_selected():
        selections = listbox.curselection()
        if not selections:
            messagebox.showwarning("No selection", "Select files to download.")
            return

        dst_dir = filedialog.askdirectory(title="Select Download Location")
        if not dst_dir:
            return

        for i in selections:
            name = listbox.get(i)
            if name == "[Intruder Logs]":
                messagebox.showinfo("Info", "Use 'View Intruder Logs' to access intruder data.")
                continue
            
            if name in vault_storage.vault_data:
                try:
                    file_data = vault_storage.vault_data[name]
                    file_content = base64.b64decode(file_data["content"])
                    
                    dest_path = os.path.join(dst_dir, name)
                    with open(dest_path, 'wb') as f:
                        f.write(file_content)
                except Exception as e:
                    messagebox.showerror("Download Error", f"Could not download {name}: {e}")
        
        messagebox.showinfo("Downloaded", f"Files saved to:\n{dst_dir}")

    def delete_selected():
        selections = listbox.curselection()
        if not selections:
            messagebox.showwarning("No selection", "Select files to delete.")
            return

        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete selected items?")
        if not confirm:
            return

        for i in selections:
            name = listbox.get(i)
            if name == "[Intruder Logs]":
                messagebox.showwarning("Restricted", "You cannot delete intruder logs.")
                continue
            
            if name in vault_storage.vault_data:
                del vault_storage.vault_data[name]
        
        vault_storage.save_to_disk()
        messagebox.showinfo("Success", "Items deleted from vault.")
        refresh_list()

    def open_selected():
        selections = listbox.curselection()
        if not selections:
            messagebox.showwarning("No selection", "Select a file to open.")
            return

        if len(selections) > 1:
            messagebox.showinfo("Info", "Only one item can be opened at a time.")
            return

        name = listbox.get(selections[0])
        if name == "[Intruder Logs]":
            view_intruder_logs()
            return

        if name in vault_storage.vault_data:
            try:
                # Create temporary file
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, name)
                
                file_data = vault_storage.vault_data[name]
                file_content = base64.b64decode(file_data["content"])
                
                with open(temp_file, 'wb') as f:
                    f.write(file_content)
                
                open_with_default(temp_file)
                
                # Schedule cleanup of temp file
                def cleanup_temp():
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
                
                vault_win.after(5000, cleanup_temp)  # Clean up after 5 seconds
                
            except Exception as e:
                messagebox.showerror("Open Error", f"Could not open {name}: {e}")

    def view_intruder_logs():
        if not vault_storage.intruder_logs:
            messagebox.showinfo("No logs", "No intruder logs found.")
            return
        
        logs_win = Tk()
        logs_win.title("Intruder Logs - Photos & Screenshots")
        logs_win.geometry("800x600")
        logs_win.configure(bg="#0d1b2a")
        
        # Create main frame
        main_frame = Frame(logs_win, bg="#0d1b2a")
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Title
        Label(main_frame, text="🚨 Intruder Detection Logs", bg="#0d1b2a", fg="#e63946", 
              font=("Arial", 16, "bold")).pack(pady=10)
        
        # Create notebook for tabs
        from tkinter import ttk
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=BOTH, expand=True)
        
        # Create a tab for each intruder attempt
        for i, log in enumerate(vault_storage.intruder_logs):
            tab = Frame(notebook, bg="#0d1b2a")
            notebook.add(tab, text=f"Attempt {i+1}")
            
            # Create scrollable frame for tab content
            canvas = tk.Canvas(tab, bg="#0d1b2a")
            scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Log information
            info_frame = Frame(scrollable_frame, bg="#1b263b", relief="raised", bd=1)
            info_frame.pack(fill="x", padx=10, pady=10)
            
            Label(info_frame, text=f"Intruder Attempt {i+1}", bg="#1b263b", fg="#ffb703",
                  font=("Arial", 12, "bold")).pack(pady=5)
            
            Label(info_frame, text=f"Timestamp: {log['timestamp']}", bg="#1b263b", fg="#e0e1dd",
                  font=("Arial", 10)).pack(anchor="w", padx=10)
            
            Label(info_frame, text=f"Camera Used: {log.get('camera_available', False)}", bg="#1b263b", fg="#e0e1dd",
                  font=("Arial", 10)).pack(anchor="w", padx=10)
            
            Label(info_frame, text=f"Screenshot Taken: {log.get('screenshot_taken', False)}", bg="#1b263b", fg="#e0e1dd",
                  font=("Arial", 10)).pack(anchor="w", padx=10, pady=(0, 10))
            
            # Media display frame
            media_frame = Frame(scrollable_frame, bg="#0d1b2a")
            media_frame.pack(fill="x", padx=10, pady=10)
            
            # Create temporary directory for this session
            temp_dir = tempfile.mkdtemp()
            saved_files = save_intruder_media(log, temp_dir)
            
            if saved_files:
                Label(media_frame, text="Captured Media:", bg="#0d1b2a", fg="#ffb703",
                      font=("Arial", 11, "bold")).pack(anchor="w", pady=5)
                
                for media_type, file_path in saved_files:
                    media_btn = Button(media_frame, text=f"📷 View {media_type}", 
                                     command=lambda path=file_path: open_with_default(path),
                                     bg="#415a77", fg="#e0e1dd", font=("Arial", 9),
                                     relief="raised", width=20)
                    media_btn.pack(anchor="w", pady=2)
            else:
                Label(media_frame, text="No media captured", bg="#0d1b2a", fg="#778da9",
                      font=("Arial", 10)).pack(anchor="w", pady=5)
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Cleanup function for temp files when window closes
            def cleanup_temp_files():
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
            
            logs_win.protocol("WM_DELETE_WINDOW", lambda: [cleanup_temp_files(), logs_win.destroy()])
        
        # If no logs with media
        if not vault_storage.intruder_logs:
            empty_tab = Frame(notebook, bg="#0d1b2a")
            notebook.add(empty_tab, text="No Logs")
            Label(empty_tab, text="No intruder logs available", bg="#0d1b2a", fg="#e0e1dd",
                  font=("Arial", 12)).pack(expand=True)

    btn_frame = Frame(vault_win, bg="#0d1b2a")
    btn_frame.pack(pady=5)

    Button(btn_frame, text="Upload Files", command=upload_files, bg="#415a77", fg="#e0e1dd", 
           width=12, font=("Arial", 9, "bold"), relief="raised").grid(row=0, column=0, padx=6, pady=3)
    Button(btn_frame, text="Download", command=download_selected, bg="#778da9", fg="#0d1b2a", 
           width=12, font=("Arial", 9, "bold"), relief="raised").grid(row=0, column=1, padx=6, pady=3)
    Button(btn_frame, text="Delete", command=delete_selected, bg="#e63946", fg="#e0e1dd", 
           width=12, font=("Arial", 9, "bold"), relief="raised").grid(row=0, column=2, padx=6, pady=3)
    Button(btn_frame, text="Open", command=open_selected, bg="#ffb703", fg="#0d1b2a", 
           width=12, font=("Arial", 9, "bold"), relief="raised").grid(row=0, column=3, padx=6, pady=3)
    Button(btn_frame, text="View Intruder Logs", command=view_intruder_logs, bg="#343a40", fg="#e0e1dd", 
           width=16, font=("Arial", 9, "bold"), relief="raised").grid(row=1, column=0, columnspan=2, pady=8)

    refresh_list()
    vault_win.mainloop()

def verify_password_and_open_vault(speak_func=None):
    if "password" not in vault_storage.config_data:
        if not setup_vault(speak_func):
            return

    password = simpledialog.askstring("Vault Access", "Enter your vault password:", show='*')
    if not password:
        if speak_func:
            speak_func("Password entry cancelled.")
        return

    hashed_pw = vault_storage.config_data["password"].encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), hashed_pw):
        if speak_func:
            speak_func("Password verified. Access granted. Opening vault.")
        open_vault_gui()
    else:
        if speak_func:
            speak_func("Incorrect password. Access denied.")
        log_intruder(speak_func)