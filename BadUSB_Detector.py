# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                                                                            ║
# ║                  BADUSB DETECTOR - PERSONAL SECURITY TOOL                  ║
# ║                                                                            ║
# ║  Copyright © 2025–2026 Iman Hajibagheri                                    ║
# ║  GitHub: https://github.com/imanh2002                                      ║
# ║                                                                            ║
# ║  All rights reserved.                                                      ║
# ║                                                                            ║
# ║  Unauthorized copying, modification, distribution, or public use of this  ║
# ║  code (in whole or in part) is strictly prohibited without explicit        ║
# ║  written permission from the copyright holder.                             ║
# ║                                                                            ║
# ║  For inquiries, collaboration or permission requests:                      ║
# ║  → imanhajibagheri60@gmail.com                                             ║
# ║                                                                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

import platform
import time
import sys
import json
import os
import threading
import queue
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

WHITELIST_FILE = 'usb_whitelist.json'
LOG_FILE = 'usb_log.txt'

def load_whitelist():
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_whitelist(whitelist):
    with open(WHITELIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(whitelist, f, ensure_ascii=False, indent=2)

def is_whitelisted(serial, vid, pid, whitelist):
    for item in whitelist:
        if item.get('serial') == serial or (item.get('vid') == vid and item.get('pid') == pid):
            return True
    return False

def block_usb(device, driver):
    if 'usb-storage' in driver:
        path = "/sys/bus/usb/drivers/usb-storage/unbind"
    elif 'hid' in driver or 'usbhid' in driver:
        path = "/sys/bus/usb/drivers/usbhid/unbind"
    else:
        return False
    dev_name = device.device_path.split('/')[-1]
    try:
        with open(path, 'w') as f:
            f.write(dev_name)
        return True
    except Exception:
        return False

def allow_usb(device, driver):
    if 'usb-storage' in driver:
        path = "/sys/bus/usb/drivers/usb-storage/bind"
    elif 'hid' in driver or 'usbhid' in driver:
        path = "/sys/bus/usb/drivers/usbhid/bind"
    else:
        return False
    dev_name = device.device_path.split('/')[-1]
    try:
        with open(path, 'w') as f:
            f.write(dev_name)
        return True
    except Exception:
        return False

class CyberUSBMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BADUSB DETECTOR v1 - ROOT ACCESS")
        self.geometry("1000x720")
        self.configure(bg="#0a0e14")

        self.style = ttk.Style(self)
        self.apply_cyber_theme()

        self.whitelist = load_whitelist()
        self.pending = queue.Queue()          # background → main thread

        # ── Header / Status ───────────────────────────────────────
        header = tk.Frame(self, bg="#0a0e14")
        header.pack(fill=tk.X, padx=10, pady=(10,0))

        tk.Label(
            header, text="BADUSB DETECTOR", fg="#00ff41", bg="#0a0e14",
            font=("Courier", 22, "bold")
        ).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="SYSTEM ARMED | MONITORING USB BUS")
        ttk.Label(header, textvariable=self.status_var, foreground="#00ff9f").pack(side=tk.RIGHT)

        # ── Log Area (matrix style) ───────────────────────────────
        self.log_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=("Courier", 11),
            bg="#0d1117", fg="#00ff41", insertbackground="#00ff41",
            selectbackground="#003300", selectforeground="#00ff41",
            relief="flat", bd=0
        )
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.log(">>> SOURCE: https://github.com/imanh2002")
        self.log(">>> SYSTEM INITIALIZED")
        self.log(f">>> OS DETECTED: {platform.system()}")
        self.log(">>> WHITELIST LOADED → " + str(len(self.whitelist)) + " entries")

        self.after(250, self.process_queue)

        self.os_type = platform.system()
        if self.os_type == 'Linux':
            if os.geteuid() != 0:
                self.log("!!! ERROR: ROOT PRIVILEGES REQUIRED FOR USB CONTROL")
            self.init_linux()
        elif self.os_type == 'Windows':
            self.init_windows()
        else:
            self.log("!!! LIMITED SUPPORT ON THIS PLATFORM")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def apply_cyber_theme(self):
        bg = "#0a0e14"
        fg = "#00ff41"
        accent = "#00eaff"
        select = "#004d26"

        self.style.configure("TLabel", background=bg, foreground=fg, font=("Courier", 11))
        self.style.configure("TFrame", background=bg)
        self.style.configure("Horizontal.TProgressbar", background=accent)

        self.option_add("*Dialog.msg.font", "Courier 11")
        self.option_add("*TButton*font", "Courier 10 bold")
        self.option_add("*background", bg)
        self.option_add("*foreground", fg)
        self.option_add("*activeBackground", "#003b1f")
        self.option_add("*activeForeground", accent)

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_text.see(tk.END)

    def on_close(self):
        if messagebox.askyesno("TERMINATE?", "SHUT DOWN MONITOR?"):
            self.destroy()

    def process_queue(self):
        try:
            while not self.pending.empty():
                info = self.pending.get_nowait()
                self.show_approval_dialog(info)
        except queue.Empty:
            pass
        self.after(250, self.process_queue)

    def show_approval_dialog(self, info):
        serial = info.get('serial', 'UNKNOWN')
        vid    = info.get('vid',    '????')
        pid    = info.get('pid',    '????')
        model  = info.get('model',  'UNKNOWN')
        vendor = info.get('vendor', 'UNKNOWN')
        path   = info.get('path',   'UNKNOWN')
        driver = info.get('driver', 'UNKNOWN')
        devtype = info.get('devtype', 'UNKNOWN')

        msg = (
            "UNKNOWN USB DEVICE DETECTED\n"
            "───────────────────────────────\n\n"
            f"PATH   : {path}\n"
            f"SERIAL : {serial}\n"
            f"VID:PID: {vid}:{pid}\n"
            f"MODEL  : {model}\n"
            f"VENDOR : {vendor}\n"
            f"DRIVER : {driver}\n"
            f"TYPE   : {devtype}\n\n"
            "ALLOW CONNECTION?   (auto-allow in 60s)"
        )

        dialog = tk.Toplevel(self)
        dialog.title("SECURITY ALERT")
        dialog.configure(bg="#0a0e14")
        dialog.geometry("520x420")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(
            dialog, text="SECURITY ALERT", fg="#ff004d", bg="#0a0e14",
            font=("Courier", 16, "bold")
        ).pack(pady=10)

        tk.Label(
            dialog, text=msg, fg="#00ff9f", bg="#0a0e14",
            font=("Courier", 11), justify="left", anchor="w"
        ).pack(padx=20, pady=5, fill=tk.X)

        result = [None]

        def on_yes():
            result[0] = True
            dialog.destroy()

        def on_no():
            result[0] = False
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg="#0a0e14")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="ALLOW [Y]", command=on_yes, style="Accent.TButton").pack(side=tk.LEFT, padx=30)
        ttk.Button(btn_frame, text="BLOCK [N]", command=on_no).pack(side=tk.RIGHT, padx=30)

        def auto_allow():
            if result[0] is None:
                result[0] = True
                dialog.destroy()
                self.log("AUTO-ALLOW TRIGGERED AFTER TIMEOUT")

        dialog.after(60000, auto_allow)

        self.wait_window(dialog)

        allowed = result[0] if result[0] is not None else True

        if allowed:
            if 'device' in info:
                allow_usb(info['device'], info['driver'])
            self.whitelist.append({'serial': serial, 'vid': vid, 'pid': pid})
            save_whitelist(self.whitelist)
            self.log(f"DEVICE AUTHORIZED → {serial}  {vid}:{pid}")
        else:
            self.log(f"DEVICE BLOCKED → {serial}  {vid}:{pid}")

        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{time.ctime()} | {serial} | {vid}:{pid} | Allowed: {allowed}\n")

    def queue_device(self, info):
        self.pending.put(info)
        self.log(f"DEVICE QUEUED → {info.get('serial','?')}  {info.get('vid','?')}:{info.get('pid','?')}  TYPE: {info.get('devtype','?')}")

    def init_linux(self):
        try:
            import pyudev
        except ImportError:
            self.log("pyudev MISSING → pip install pyudev")
            return

        context = pyudev.Context()

        # Process all USB devices, including system ones
        for dev in context.list_devices(subsystem='usb'):
            driver = dev.properties.get('DRIVER', '').lower()
            parent = dev.parent
            props = parent.properties if parent else dev.properties
            serial = props.get('ID_SERIAL', 'UNKNOWN')
            vid = props.get('ID_VENDOR_ID', '????')
            pid = props.get('ID_MODEL_ID', '????')
            model = props.get('ID_MODEL', 'UNKNOWN')
            vendor = props.get('ID_VENDOR', 'UNKNOWN')
            devtype = dev.properties.get('DEVTYPE', 'UNKNOWN')

            if is_whitelisted(serial, vid, pid, self.whitelist):
                if driver:
                    allow_usb(dev, driver)
                continue

            blocked = False
            if driver:
                blocked = block_usb(dev, driver)

            self.queue_device({
                'device': dev,
                'driver': driver,
                'serial': serial,
                'vid': vid,
                'pid': pid,
                'model': model,
                'vendor': vendor,
                'path': dev.device_path,
                'devtype': devtype
            })

        # Monitor for new USB devices
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')

        def watch():
            for dev in iter(monitor.poll, None):
                if dev.action != 'add':
                    continue
                driver = dev.properties.get('DRIVER', '').lower()
                parent = dev.parent
                props = parent.properties if parent else dev.properties
                serial = props.get('ID_SERIAL', 'UNKNOWN')
                vid = props.get('ID_VENDOR_ID', '????')
                pid = props.get('ID_MODEL_ID', '????')
                model = props.get('ID_MODEL', 'UNKNOWN')
                vendor = props.get('ID_VENDOR', 'UNKNOWN')
                devtype = dev.properties.get('DEVTYPE', 'UNKNOWN')

                blocked = False
                if driver:
                    blocked = block_usb(dev, driver)

                self.queue_device({
                    'device': dev,
                    'driver': driver,
                    'serial': serial,
                    'vid': vid,
                    'pid': pid,
                    'model': model,
                    'vendor': vendor,
                    'path': dev.device_path,
                    'devtype': devtype
                })

        threading.Thread(target=watch, daemon=True).start()
        self.log(">>> USB BUS MONITOR ACTIVE (LINUX MODE - ALL USBs)")

    def init_windows(self):
        try:
            import wmi
        except ImportError:
            self.log("wmi MISSING → pip install wmi")
            return

        c = wmi.WMI()
        watcher = c.Win32_PnPEntity.watch_for("creation")

        def watch():
            while True:
                try:
                    dev = watcher(timeout_ms=1500)
                    if not dev:
                        continue
                    dev_id = dev.DeviceID or ""
                    parts = dev_id.split('\\')
                    serial = parts[-1] if len(parts) > 2 else "UNKNOWN"
                    vid_pid = parts[1] if len(parts) > 1 else "UNKNOWN"
                    vid, pid = vid_pid.split('&')[:2] if '&' in vid_pid else ("????", "????")
                    model = dev.Caption or "UNKNOWN"
                    vendor = dev.Manufacturer or "UNKNOWN"
                    devtype = dev.PNPClass or "UNKNOWN"

                    self.queue_device({
                        'serial': serial,
                        'vid': vid,
                        'pid': pid,
                        'model': model,
                        'vendor': vendor,
                        'path': dev_id,
                        'devtype': devtype
                    })
                except:
                    pass

        threading.Thread(target=watch, daemon=True).start()
        self.log(">>> WINDOWS DETECTION MODE (ALL USBs - MANUAL BLOCK REQUIRED)")

if __name__ == "__main__":
    app = CyberUSBMonitor()
    app.mainloop()
