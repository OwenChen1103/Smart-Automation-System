# Smart Automation System

A concise, practical desktop automation tool that allows you to easily automate repetitive computer operations.

## ✨ Main Features

- **Precise Position Selection** - Easily select positions to click or operate
- **Multiple Operation Types** - Supports clicking, text input, monitoring, and other operations
- **Real-time Position Display** - Real-time display of mouse position for precise positioning
- **Clean Interface** - Intuitive and easy-to-use graphical interface
- **Stable and Reliable** - Based on mature PySide6 and pyautogui technology

## 🚀 Quick Start

### Install Dependencies
```bash
pip3 install -r requirements.txt
```

### Start the System
```bash
python3 smart_automation.py
```

### Use Precise Selector
```bash
python3 original_precise_selector.py
```

## 🎯 How to Use

### 1. Start Smart Automation System
- Run `python3 smart_automation.py`
- Click "➕ Add Element" to start adding automation steps

### 2. Precise Position Selection
- Move mouse to target position
- Click "📍 Get Current Position" button
- Select element type and set parameters

### 3. Execute Automation
- After adding all steps
- Click "🚀 Start Automation" to execute

## 📁 File Description

- `smart_automation.py` - Main automation system
- `original_precise_selector.py` - Precise position selector
- `start_smart.py` - Quick start script
- `requirements.txt` - Dependency package list

## 🎯 Supported Operation Types

- **Button (Click)** - Click specified position
- **Input Box (Text Input)** - Input text at specified position
- **Text Area (Monitor Text)** - Monitor text in specified area
- **Image Area (Monitor Image)** - Monitor image in specified area
- **Custom Area (Click)** - Custom click operation

## 🛠️ Tech Stack

### **Core Technologies**
- **Python 3.7+** - Primary programming language
- **PySide6** - Modern Qt-based GUI framework
- **pyautogui** - Cross-platform GUI automation library
- **OpenCV (cv2)** - Computer vision and image processing
- **Pillow (PIL)** - Python Imaging Library for image handling
- **NumPy** - Numerical computing and array operations

### **OCR & Text Recognition**
- **Tesseract OCR** - Optical Character Recognition engine
- **pytesseract** - Python wrapper for Tesseract OCR

### **Image Processing & Computer Vision**
- **OpenCV-Python** - Real-time computer vision library
- **Template Matching** - Image detection and matching algorithms
- **Screenshot Capture** - Real-time screen capture capabilities

### **GUI & User Interface**
- **PySide6/Qt6** - Modern cross-platform GUI framework
- **QThread** - Multi-threading for non-blocking operations
- **QTimer** - Real-time updates and monitoring
- **Signal/Slot** - Event-driven programming model

### **System Integration**
- **Cross-platform Support** - macOS, Windows, Linux
- **Screen Access APIs** - Native OS screen capture
- **Mouse/Keyboard Control** - System-level input simulation

## 🔧 System Requirements

- **Python 3.7+** - Core runtime environment
- **Tesseract OCR** - For text recognition features
- **Screen Access Permission** - Required for automation
- **Operating System** - macOS / Windows / Linux

## 📝 Usage Examples

### Automatic Website Login
1. Add "Input Box (Text Input)" element - input username
2. Add "Input Box (Text Input)" element - input password
3. Add "Button (Click)" element - click login button

### Automatic Form Filling
1. Add multiple "Input Box (Text Input)" elements
2. Add "Button (Click)" element - submit form

## 🎯 Special Features

- **Precise Positioning** - Pixel-level accuracy
- **Real-time Feedback** - Instant operation status display
- **Error Handling** - Comprehensive error prompts
- **Logging** - Detailed operation logs

---

**Making automation simple!** 🎯✨ 