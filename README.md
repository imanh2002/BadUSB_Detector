# 🛡️ BADUSB DETECTOR  
### 🔐 Personal USB Security & Monitoring Tool

> **Protect your system against malicious USB attacks (BadUSB).**  
> Real-time USB monitoring • User authorization • Kernel-level USB control (Linux)

---

## 🚨 What is BadUSB?

**BadUSB** is a dangerous hardware-based attack where a USB device can:
- 🧠 Impersonate a keyboard (HID)
- ⚡ Execute commands automatically
- 🕵️ Bypass antivirus and OS security
- 🔓 Compromise the system without user consent

**BADUSB DETECTOR** is designed to stop these threats *before* they can cause damage.

---

## ✨ Features

### 🔍 Advanced USB Monitoring
✔ Detects **all USB devices** (Storage / HID / System)  
✔ Reads **VID / PID / Serial / Vendor / Driver**  
✔ Monitors **already connected & newly added** devices  

### 🔐 Security Control
✔ Automatically blocks unknown USB devices  
✔ Interactive **Allow / Block** security alert  
✔ Persistent **Whitelist** for trusted devices  
✔ Full USB activity logging  

### 🖥️ Cyber-Style GUI
✔ Matrix-inspired cyber interface  
✔ Live system status messages  
✔ Auto-Allow timeout mechanism  
✔ Lightweight & fast (Tkinter)

### 🐧🪟 OS Support

| Operating System | Support |
|------------------|---------|
| **Linux (Root)** | ✅ Full USB control (bind / unbind) |
| **Windows** | ⚠️ Detection only (manual blocking required) |

---

## 🧠 How It Works

```text
USB Device Connected
        ↓
Device Identification
(VID / PID / Serial)
        ↓
Whitelist Verification
   ├─ Known → Allow
   └─ Unknown → Block & Alert
                       ↓
                 User Decision
