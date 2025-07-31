#!/usr/bin/env python3
"""
Smart Automation Assistant Startup Script
"""

import os
import sys
import subprocess

def main():
    print("🤖 Smart Automation Assistant")
    print("=" * 40)
    print()
    
    # Check dependencies
    try:
        import PySide6
        import pyautogui
        import cv2
        import numpy as np
        print("✅ All dependency packages installed")
    except ImportError as e:
        print(f"❌ Missing dependency package: {e}")
        print("Please run: pip install -r requirements.txt")
        return
    
    # Check files
    if not os.path.exists("smart_automation.py"):
        print("❌ Cannot find smart_automation.py file")
        return
    
    print("🚀 Starting Smart Automation Assistant...")
    print()
    print("📋 Usage Instructions:")
    print("1. Open the website or application you want to automate")
    print("2. Click the '➕ Add Element' button")
    print("3. Select element type and set parameters")
    print("4. Click '🎯 Select Element' and move mouse to target position")
    print("5. Repeat steps 2-4 to add more elements")
    print("6. Click '▶️ Start Automation' to begin execution")
    print()
    print("💡 Tip: The system will automatically record your operation sequence")
    print()
    
    # Start application
    try:
        subprocess.run([sys.executable, "smart_automation.py"])
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Startup failed: {e}")

if __name__ == "__main__":
    main() 