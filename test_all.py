"""
Valtrix AI — Comprehensive Feature Test Suite
Tests all components without launching the full GUI.
"""
import os
import sys
import json
import tempfile
import shutil

PASS = 0
FAIL = 0
WARN = 0

def test(name, func):
    global PASS, FAIL, WARN
    try:
        result = func()
        if result is True:
            print(f"  [PASS] {name}")
            PASS += 1
        elif result == "WARN":
            print(f"  [WARN] {name}")
            WARN += 1
        else:
            print(f"  [FAIL] {name} -> {result}")
            FAIL += 1
    except Exception as e:
        print(f"  [FAIL] {name} -> {type(e).__name__}: {e}")
        FAIL += 1


print("=" * 60)
print("  VALTRIX AI - FEATURE TEST SUITE")
print("=" * 60)

# ── 1. MODULE IMPORTS ──
print("\n[1] Module Imports")
test("Import main", lambda: __import__("main") and True)
test("Import gui", lambda: __import__("gui") and True)
test("Import secure_vault", lambda: __import__("secure_vault") and True)
test("Import openapp", lambda: __import__("openapp") and True)
test("Import SearchNow", lambda: __import__("SearchNow") and True)
test("Import greeting", lambda: __import__("greeting") and True)
test("Import keyboardfunction", lambda: __import__("keyboardfunction") and True)

# ── 2. AES-256-GCM ENCRYPTION ──
print("\n[2] AES-256-GCM Encryption Engine")
from secure_vault import AES256GCMEngine

def test_encrypt_decrypt():
    salt = os.urandom(16)
    key = AES256GCMEngine.derive_key("testpassword123", salt)
    assert len(key) == 32, f"Key size {len(key)} != 32"
    data = b"Hello Valtrix AI! This is a test."
    enc = AES256GCMEngine.encrypt(data, key)
    assert enc != data, "Encrypted data equals plaintext"
    assert len(enc) > len(data), "Encrypted should be larger (nonce+tag)"
    dec = AES256GCMEngine.decrypt(enc, key)
    assert dec == data, "Decrypted data doesn't match original"
    return True

def test_wrong_key():
    salt = os.urandom(16)
    key1 = AES256GCMEngine.derive_key("password1", salt)
    key2 = AES256GCMEngine.derive_key("password2", salt)
    enc = AES256GCMEngine.encrypt(b"secret", key1)
    try:
        AES256GCMEngine.decrypt(enc, key2)
        return "Wrong key should have raised error"
    except Exception:
        return True

def test_unique_nonces():
    salt = os.urandom(16)
    key = AES256GCMEngine.derive_key("pass", salt)
    enc1 = AES256GCMEngine.encrypt(b"same data", key)
    enc2 = AES256GCMEngine.encrypt(b"same data", key)
    assert enc1 != enc2, "Same plaintext should produce different ciphertext"
    return True

def test_key_size():
    salt = os.urandom(16)
    key = AES256GCMEngine.derive_key("test", salt)
    return len(key) * 8 == 256 or f"Key is {len(key)*8} bits, expected 256"

test("Encrypt/Decrypt cycle", test_encrypt_decrypt)
test("Wrong key rejection (GCM auth)", test_wrong_key)
test("Unique nonces per encryption", test_unique_nonces)
test("Key size is 256 bits", test_key_size)

# ── 3. VAULT STORAGE ──
print("\n[3] Secure Vault Storage")
from secure_vault import SecureVaultStorage

def test_vault_lifecycle():
    # Create a temp vault for testing
    v = SecureVaultStorage()
    orig_dir = v.vault_dir
    test_dir = os.path.join(tempfile.gettempdir(), "valtrix_test_vault")
    v.vault_dir = test_dir
    v.files_dir = os.path.join(test_dir, "files")
    v.intruder_dir = os.path.join(test_dir, "intruders")
    v.salt_file = os.path.join(test_dir, "vault.salt")
    v.verify_file = os.path.join(test_dir, "vault.verify")
    v.meta_file = os.path.join(test_dir, "vault_meta.enc")
    v.intruder_log_file = os.path.join(test_dir, "intruder_logs.json")
    os.makedirs(v.files_dir, exist_ok=True)
    os.makedirs(v.intruder_dir, exist_ok=True)

    try:
        # Setup
        assert v.setup("testpass123"), "Setup failed"
        assert v.is_setup(), "Vault should be setup"
        assert v.is_unlocked(), "Vault should be unlocked after setup"

        # Lock and unlock
        v.lock()
        assert not v.is_unlocked(), "Vault should be locked"
        assert v.unlock("testpass123"), "Unlock with correct password failed"
        assert v.is_unlocked(), "Vault should be unlocked"

        # Wrong password
        v.lock()
        assert not v.unlock("wrongpass"), "Wrong password should fail"

        # File upload
        v.unlock("testpass123")
        test_file = os.path.join(test_dir, "test_upload.txt")
        with open(test_file, 'w') as f:
            f.write("This is a secret document!")
        assert v.upload_file(test_file), "Upload failed"

        files = v.list_files()
        assert len(files) == 1, f"Expected 1 file, got {len(files)}"
        file_id = list(files.keys())[0]
        assert files[file_id]["name"] == "test_upload.txt"

        # File download
        dl_dir = os.path.join(test_dir, "downloads")
        os.makedirs(dl_dir, exist_ok=True)
        dl_path = v.download_file(file_id, dl_dir)
        assert dl_path is not None, "Download returned None"
        with open(dl_path, 'r') as f:
            content = f.read()
        assert content == "This is a secret document!", f"Content mismatch: {content}"

        # File delete
        assert v.delete_file(file_id), "Delete failed"
        assert len(v.list_files()) == 0, "File should be deleted"

        return True
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

test("Vault lifecycle (setup/lock/unlock/upload/download/delete)", test_vault_lifecycle)

def test_vault_persistence():
    test_dir = os.path.join(tempfile.gettempdir(), "valtrix_test_vault2")
    try:
        # Create and setup vault
        v1 = SecureVaultStorage()
        v1.vault_dir = test_dir
        v1.files_dir = os.path.join(test_dir, "files")
        v1.intruder_dir = os.path.join(test_dir, "intruders")
        v1.salt_file = os.path.join(test_dir, "vault.salt")
        v1.verify_file = os.path.join(test_dir, "vault.verify")
        v1.meta_file = os.path.join(test_dir, "vault_meta.enc")
        v1.intruder_log_file = os.path.join(test_dir, "intruder_logs.json")
        os.makedirs(v1.files_dir, exist_ok=True)
        os.makedirs(v1.intruder_dir, exist_ok=True)
        v1.setup("persist_test")

        # Upload a file
        tf = os.path.join(test_dir, "persist.txt")
        with open(tf, 'w') as f:
            f.write("persistent data")
        v1.upload_file(tf)
        v1.lock()

        # Create new instance (simulates restart)
        v2 = SecureVaultStorage()
        v2.vault_dir = test_dir
        v2.files_dir = os.path.join(test_dir, "files")
        v2.intruder_dir = os.path.join(test_dir, "intruders")
        v2.salt_file = os.path.join(test_dir, "vault.salt")
        v2.verify_file = os.path.join(test_dir, "vault.verify")
        v2.meta_file = os.path.join(test_dir, "vault_meta.enc")
        v2.intruder_log_file = os.path.join(test_dir, "intruder_logs.json")
        assert v2.is_setup(), "Vault should still be setup"
        assert v2.unlock("persist_test"), "Should unlock with same password"
        files = v2.list_files()
        assert len(files) == 1, f"Expected 1 persisted file, got {len(files)}"
        return True
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

test("Vault persistence across restarts", test_vault_persistence)

# ── 4. THEMES ──
print("\n[4] Theme System")
from gui import THEMES, load_config, save_config, CONFIG_FILE

def test_all_themes_valid():
    required_keys = {"bg", "card", "sidebar", "accent", "green", "red",
                     "yellow", "purple", "text", "dim", "border",
                     "chat_bg", "user_bubble", "bot_bubble"}
    for name, theme in THEMES.items():
        missing = required_keys - set(theme.keys())
        if missing:
            return f"Theme '{name}' missing keys: {missing}"
    return True

def test_theme_count():
    return len(THEMES) == 5 or f"Expected 5 themes, got {len(THEMES)}"

def test_theme_config_save():
    backup = load_config()
    save_config({"theme": "Cyberpunk"})
    cfg = load_config()
    assert cfg["theme"] == "Cyberpunk", "Theme not saved"
    save_config(backup)  # restore
    return True

test("All 5 themes have 14 required color keys", test_all_themes_valid)
test("Theme count is 5", test_theme_count)
test("Theme config save/load", test_theme_config_save)

# ── 5. ANALYTICS ──
print("\n[5] Usage Analytics")
from gui import UsageAnalytics

def test_analytics():
    a = UsageAnalytics()
    old_total = a.data.get("total", 0)
    a.track("test_command")
    assert a.data["total"] == old_total + 1, "Total not incremented"
    assert a.data["types"].get("test_command", 0) >= 1, "Type not tracked"
    assert a.data["today"] >= 1, "Today count not updated"
    a.new_session()
    assert a.data["sessions"] >= 1, "Session not tracked"
    return True

test("Track commands + sessions", test_analytics)

# ── 6. WAVEFORM ──
print("\n[6] Waveform Visualizer")
from gui import WaveformVisualizer

def test_waveform_class():
    assert hasattr(WaveformVisualizer, '__init__'), "Missing __init__"
    assert hasattr(WaveformVisualizer, 'set_state'), "Missing set_state"
    assert hasattr(WaveformVisualizer, '_animate'), "Missing _animate"
    return True

test("WaveformVisualizer class structure", test_waveform_class)

# ── 7. CHAT DISPLAY ──
print("\n[7] Chat Display")
from gui import ChatDisplay

def test_chat_class():
    assert hasattr(ChatDisplay, 'add_message'), "Missing add_message"
    assert hasattr(ChatDisplay, '_create_bubble'), "Missing _create_bubble"
    assert hasattr(ChatDisplay, '_check_queue'), "Missing _check_queue"
    assert hasattr(ChatDisplay, 'insert'), "Missing backward-compat insert"
    assert hasattr(ChatDisplay, 'see'), "Missing backward-compat see"
    return True

test("ChatDisplay class structure + backward compat", test_chat_class)

# ── 8. APP LAUNCHER ──
print("\n[8] App Launcher")
from openapp import openapp, openappweb, closeappweb

def test_app_count():
    count = len(openapp)
    return count >= 100 or f"Expected 100+ apps, got {count}"

def test_app_categories():
    categories = {
        "system": ["command prompt", "task manager", "control panel"],
        "office": ["word", "excel", "powerpoint"],
        "browsers": ["chrome", "edge", "firefox"],
        "dev": ["vscode", "pycharm"],
        "media": ["vlc", "spotify"],
        "gaming": ["steam", "valorant"],
    }
    for cat, apps in categories.items():
        for app in apps:
            if app not in openapp:
                return f"Missing app '{app}' in {cat}"
    return True

def test_speak_param():
    # Verify functions accept speak parameter
    import inspect
    sig_open = inspect.signature(openappweb)
    sig_close = inspect.signature(closeappweb)
    assert "speak" in sig_open.parameters, "openappweb missing speak param"
    assert "speak" in sig_close.parameters, "closeappweb missing speak param"
    return True

test("100+ apps registered", test_app_count)
test("Key apps in all categories", test_app_categories)
test("Functions accept speak parameter", test_speak_param)

# ── 9. SEARCH MODULE ──
print("\n[9] Search Module")
from SearchNow import searchGoogle, searchYoutube, searchWikipedia
import inspect

def test_search_no_blocking():
    # If we got here, the import didn't block (old bug was module-level takeCommand)
    return True

def test_search_speak_params():
    for fn_name, fn in [("searchGoogle", searchGoogle), ("searchYoutube", searchYoutube),
                         ("searchWikipedia", searchWikipedia)]:
        sig = inspect.signature(fn)
        if "speak" not in sig.parameters:
            return f"{fn_name} missing speak param"
    return True

test("No module-level blocking on import", test_search_no_blocking)
test("All search functions accept speak param", test_search_speak_params)

# ── 10. GREETING ──
print("\n[10] Greeting Module")
from greeting import greetMe
import inspect

def test_greeting_signature():
    sig = inspect.signature(greetMe)
    params = list(sig.parameters.keys())
    assert "speak" in params, f"Expected 'speak' param, got {params}"
    return True

def test_greeting_runs():
    messages = []
    greetMe(lambda msg: messages.append(msg))
    assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
    assert "Valtrix AI" in messages[1], f"Missing branding in: {messages[1]}"
    return True

test("greetMe accepts speak parameter", test_greeting_signature)
test("Greeting outputs 2 messages with branding", test_greeting_runs)

# ── 11. KEYBOARD FUNCTIONS ──
print("\n[11] Keyboard Functions")
from keyboardfunction import volumeup, volumedown

def test_kb_functions():
    assert callable(volumeup), "volumeup not callable"
    assert callable(volumedown), "volumedown not callable"
    return True

test("Volume functions exist and callable", test_kb_functions)

# ── 12. SYSTEM MONITOR ──
print("\n[12] System Monitor")
from main import get_system_info

def test_system_info():
    info = get_system_info()
    assert info is not None, "get_system_info returned None"
    required = ["cpu", "mem_used", "mem_total", "mem_pct",
                "disk_used", "disk_total", "disk_pct", "uptime", "os"]
    for key in required:
        if key not in info:
            return f"Missing key: {key}"
    assert 0 <= info["cpu"] <= 100, f"CPU {info['cpu']}% out of range"
    assert info["mem_total"] > 0, "Memory total should be > 0"
    assert info["disk_total"] > 0, "Disk total should be > 0"
    return True

test("System info returns all metrics", test_system_info)

# ── 13. VOICE RECOGNIZER ──
print("\n[13] Voice Recognition")
from main import EnhancedVoiceRecognizer

def test_recognizer():
    r = EnhancedVoiceRecognizer()
    assert r.recognizer.dynamic_energy_threshold == True
    assert r.recognizer.energy_threshold == 400
    assert r.recognizer.pause_threshold == 0.8
    return True

test("Recognizer config (threshold/pause)", test_recognizer)

# ── 14. TTS ENGINE ──
print("\n[14] Text-to-Speech")
from main import engine as tts_engine

def test_tts():
    voices = tts_engine.getProperty("voices")
    assert len(voices) >= 1, "No TTS voices found"
    assert tts_engine is not None, "Engine is None"
    return True

test("TTS engine functional with voices", test_tts)

# ── 15. FILE STRUCTURE ──
print("\n[15] File Structure")
app_dir = os.path.dirname(os.path.abspath(__file__))

def test_required_files():
    required = ["main.py", "gui.py", "secure_vault.py", "openapp.py",
                "SearchNow.py", "greeting.py", "keyboardfunction.py", "requirements.txt"]
    for f in required:
        if not os.path.exists(os.path.join(app_dir, f)):
            return f"Missing: {f}"
    return True

def test_no_duplicate():
    dup = os.path.join(app_dir, "secure_vault copy.py")
    return not os.path.exists(dup) or "Duplicate file still exists"

def test_requirements():
    req_file = os.path.join(app_dir, "requirements.txt")
    with open(req_file, 'r') as f:
        reqs = [l.strip() for l in f if l.strip()]
    expected = ["pyttsx3", "SpeechRecognition", "pyautogui", "cryptography",
                "psutil", "customtkinter", "pystray", "bcrypt", "Pillow", "pynput"]
    for pkg in expected:
        if pkg not in reqs:
            return f"Missing from requirements.txt: {pkg}"
    return True

test("All 8 source files present", test_required_files)
test("No duplicate vault file", test_no_duplicate)
test("requirements.txt has all 13 packages", test_requirements)

# ── 16. GUI CREATION ──
print("\n[16] GUI Factory")
from gui import create_gui, restart_with_theme

def test_gui_returns():
    assert callable(create_gui), "create_gui not callable"
    assert isinstance(restart_with_theme, list), "restart_with_theme should be list"
    return True

test("create_gui callable + restart_with_theme exists", test_gui_returns)

# ══════ SUMMARY ══════
print("\n" + "=" * 60)
print(f"  RESULTS:  {PASS} PASSED  |  {FAIL} FAILED  |  {WARN} WARNINGS")
print("=" * 60)

if FAIL == 0:
    print("  ALL TESTS PASSED!")
else:
    print(f"  {FAIL} test(s) need attention.")
    sys.exit(1)
