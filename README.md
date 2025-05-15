# Automated Betting Monitor 🎲

This is a desktop automation tool developed with PySide6, OpenCV, and pyautogui. It monitors a visual betting interface, detects game states, and places automated bets based on user-defined strategies. A logging system records each betting round with time, result, and betting details.

## 🔧 Features
- 🖥 GUI interface for importing screen elements
- 🧩 Image-based calibration using OpenCV
- 🤖 Automated betting logic with randomized timing
- 📝 CSV logger for detailed session records
- 📈 Live result capture and progress tracking

## 🛠 Tech Stack
- Python
- PySide6 (GUI)
- OpenCV (Template Matching)
- pyautogui (Screen automation)

## 📁 Files
- `main.py` - Entry point & GUI control
- `Correction_Tool.py` - Screen element calibration
- `BettingOperation.py` - Betting strategy engine
- `BettingLogger.py` - CSV log writer
- `ResultWindow.py` - Live game monitor and result display
- `templates/` - Template images for UI calibration

## 🚀 How to Run
```bash
pip install -r requirements.txt
python main.py
