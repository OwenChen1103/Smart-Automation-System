#!/usr/bin/env python3
"""
Smart Automation Assistant
Simplified template mode - users directly select elements for automation
"""

import os
import sys
import json
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QListWidget, 
                             QListWidgetItem, QDialog, QComboBox, QLineEdit,
                             QMessageBox, QFrame, QTextEdit, QSpinBox)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
import pyautogui
import cv2
import numpy as np

class ElementSelector(QDialog):
    """Element Selector - Let users select elements on screen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Element")
        self.setFixedSize(400, 300)
        self.selected_element = None
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        instruction = QLabel("Please select the element type to automate:")
        instruction.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(instruction)
        
        # Element type selection
        self.element_type = QComboBox()
        self.element_type.addItems([
            "Button (Click)",
            "Input Box (Text Input)", 
            "Text Area (Monitor Text)",
            "Image Area (Monitor Image)",
            "Custom Area (Click)"
        ])
        self.element_type.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.element_type)
        
        # Parameter input
        self.param_label = QLabel("Parameter Settings:")
        self.param_label.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(self.param_label)
        
        self.param_input = QLineEdit()
        self.param_input.setPlaceholderText("Enter text, wait time, etc.")
        self.param_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.param_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_btn = QPushButton("🎯 Select Element")
        self.select_btn.clicked.connect(self.select_element)
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Update parameter hints
        self.element_type.currentTextChanged.connect(self.update_param_hint)
        self.update_param_hint()
        
    def update_param_hint(self):
        """Update parameter input hints"""
        current_type = self.element_type.currentText()
        
        if "Text Input" in current_type:
            self.param_input.setPlaceholderText("Text to input")
        elif "Monitor Text" in current_type:
            self.param_input.setPlaceholderText("Text to search for (e.g.: 'Login', 'Submit')")
        elif "Monitor Image" in current_type:
            self.param_input.setPlaceholderText("Image filename to match (e.g.: button.png)")
        elif "Custom Area" in current_type:
            self.param_input.setPlaceholderText("Custom coordinates (e.g.: 100,200) or wait:2")
        elif "Wait" in current_type:
            self.param_input.setPlaceholderText("Wait seconds (e.g.: 2)")
        else:
            self.param_input.setPlaceholderText("Parameter (optional)")
            
    def select_element(self):
        """Select element"""
        try:
            self.hide()  # Hide dialog
            
            current_type = self.element_type.currentText()
            
            if "Monitor Text" in current_type or "Monitor Image" in current_type:
                # For monitoring elements, select a rectangular area
                QMessageBox.information(self, "Area Selection Instructions", 
                    "Please follow these steps to select a monitoring area:\n\n"
                    "1. Move your mouse to the TOP-LEFT corner of the area\n"
                    "2. Keep the mouse still\n"
                    "3. The system will record this position in 3 seconds\n"
                    "4. Then move to the BOTTOM-RIGHT corner\n"
                    "5. The system will record the second position\n\n"
                    "💡 Tip: This creates a rectangular monitoring area")
                
                # Get first position (top-left)
                for i in range(5, 0, -1):
                    print(f"Select TOP-LEFT corner... {i}")
                    time.sleep(1)
                
                x1, y1 = pyautogui.position()
                
                # Get second position (bottom-right)
                QMessageBox.information(self, "Second Position", 
                    f"Top-left corner recorded: ({x1}, {y1})\n\n"
                    "Now move your mouse to the BOTTOM-RIGHT corner of the area\n"
                    "and keep it still for 3 seconds...")
                
                for i in range(5, 0, -1):
                    print(f"Select BOTTOM-RIGHT corner... {i}")
                    time.sleep(1)
                
                x2, y2 = pyautogui.position()
                
                # Calculate area dimensions
                x = min(x1, x2)
                y = min(y1, y2)
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                
                # Create element information with area data
                self.selected_element = {
                    "type": current_type,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "parameter": self.param_input.text(),
                    "timestamp": time.time()
                }
                
                # Show selection confirmation
                QMessageBox.information(self, "Area Selection Confirmation", 
                    f"Selected monitoring area:\n"
                    f"Top-left: ({x}, {y})\n"
                    f"Width: {width}, Height: {height}\n\n"
                    f"Element type: {current_type}\n"
                    f"Parameter: {self.param_input.text()}\n\n"
                    "Click OK to confirm selection")
                
            else:
                # For click/input elements, select single position
                QMessageBox.information(self, "Position Selection Instructions", 
                    "Please follow these steps to select an element:\n\n"
                    "1. Move your mouse to the position you want to click\n"
                    "2. Keep the mouse still\n"
                    "3. The system will record this position in 3 seconds\n\n"
                    "💡 Tip: You can use right-click or press F12 for precise positioning")
                
                # Give user more preparation time
                for i in range(5, 0, -1):
                    print(f"Preparing to select element... {i}")
                    time.sleep(1)
                
                # Get mouse position
                x, y = pyautogui.position()
                
                # Create element information
                self.selected_element = {
                    "type": current_type,
                    "x": x,
                    "y": y,
                    "parameter": self.param_input.text(),
                    "timestamp": time.time()
                }
                
                # Show selection confirmation
                QMessageBox.information(self, "Selection Confirmation", 
                    f"Selected position: ({x}, {y})\n\n"
                    f"Element type: {current_type}\n"
                    f"Parameter: {self.param_input.text()}\n\n"
                    "Click OK to confirm selection")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to select element: {str(e)}")
            self.reject()

class AutomationThread(QThread):
    """Automation execution thread"""
    status_updated = Signal(str)
    element_processed = Signal(str)
    
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
        self.running = True
        
    def run(self):
        """Execute automation"""
        try:
            for i, element in enumerate(self.elements):
                if not self.running:
                    break
                    
                self.status_updated.emit(f"Executing element {i+1}: {element['type']}")
                
                # Execute operations based on element type
                if "Click" in element['type']:
                    # Check if it's custom area click with parameters
                    if "Custom Area" in element['type'] and element['parameter']:
                        try:
                            # Parse custom parameters (e.g., "100,200" for x,y or "wait:2" for delay)
                            params = element['parameter'].split(',')
                            if len(params) >= 2:
                                # Custom coordinates
                                x = int(params[0].strip())
                                y = int(params[1].strip())
                                pyautogui.click(x, y)
                                self.element_processed.emit(f"Custom click at ({x}, {y})")
                            else:
                                # Regular click with potential delay
                                if "wait:" in element['parameter']:
                                    wait_time = float(element['parameter'].split(':')[1])
                                    time.sleep(wait_time)
                                pyautogui.click(element['x'], element['y'])
                                self.element_processed.emit(f"Custom area click at ({element['x']}, {element['y']})")
                        except:
                            # Fallback to regular click
                            pyautogui.click(element['x'], element['y'])
                            self.element_processed.emit(f"Clicked position ({element['x']}, {element['y']})")
                    else:
                        # Regular button click
                        pyautogui.click(element['x'], element['y'])
                        self.element_processed.emit(f"Clicked position ({element['x']}, {element['y']})")
                    
                elif "Text Input" in element['type']:
                    pyautogui.click(element['x'], element['y'])
                    time.sleep(0.5)
                    pyautogui.write(element['parameter'])
                    self.element_processed.emit(f"Input text: {element['parameter']}")
                    
                elif "Monitor Text" in element['type']:
                    # Text monitoring implementation
                    try:
                        import pytesseract
                        from PIL import Image
                        
                        # Use area dimensions if available, otherwise use default area
                        if 'width' in element and 'height' in element:
                            x, y, width, height = element['x'], element['y'], element['width'], element['height']
                            self.element_processed.emit(f"📸 Monitoring text area: ({x}, {y}) {width}x{height}")
                        else:
                            # Fallback to default area around point
                            x, y = element['x'], element['y']
                            width, height = 200, 100
                            x = x - 100
                            y = y - 50
                            self.element_processed.emit(f"📸 Monitoring text area (default): ({x}, {y}) {width}x{height}")
                        
                        # Take screenshot of the area
                        screenshot = pyautogui.screenshot(region=(x, y, width, height))
                        
                        # Extract text using OCR
                        text = pytesseract.image_to_string(screenshot, lang='eng')
                        text = text.strip()
                        
                        target_text = element['parameter']
                        if target_text.lower() in text.lower():
                            self.element_processed.emit(f"✅ Target text '{target_text}' found in area")
                        else:
                            self.element_processed.emit(f"❌ Target text '{target_text}' not found. Found: '{text[:50]}...'")
                            
                    except ImportError:
                        self.element_processed.emit(f"⚠️ OCR not available. Please install: pip install pytesseract")
                    except Exception as e:
                        self.element_processed.emit(f"❌ Text monitoring failed: {str(e)}")
                    
                elif "Monitor Image" in element['type']:
                    # Image monitoring implementation
                    try:
                        import cv2
                        import numpy as np
                        
                        # Use area dimensions if available, otherwise use default area
                        if 'width' in element and 'height' in element:
                            x, y, width, height = element['x'], element['y'], element['width'], element['height']
                            self.element_processed.emit(f"📸 Monitoring image area: ({x}, {y}) {width}x{height}")
                        else:
                            # Fallback to default area around point
                            x, y = element['x'], element['y']
                            width, height = 200, 100
                            x = x - 100
                            y = y - 50
                            self.element_processed.emit(f"📸 Monitoring image area (default): ({x}, {y}) {width}x{height}")
                        
                        # Take screenshot of the area
                        screenshot = pyautogui.screenshot(region=(x, y, width, height))
                        screenshot_np = np.array(screenshot)
                        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
                        
                        # If target image is provided
                        if element['parameter'] and os.path.exists(element['parameter']):
                            target_image = cv2.imread(element['parameter'])
                            if target_image is not None:
                                # Template matching
                                result = cv2.matchTemplate(screenshot_cv, target_image, cv2.TM_CCOEFF_NORMED)
                                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                                
                                if max_val > 0.8:  # Threshold for matching
                                    self.element_processed.emit(f"✅ Target image found with confidence: {max_val:.2f}")
                                else:
                                    self.element_processed.emit(f"❌ Target image not found. Best match: {max_val:.2f}")
                            else:
                                self.element_processed.emit(f"❌ Could not load target image: {element['parameter']}")
                        else:
                            # Just monitor area for changes
                            self.element_processed.emit(f"📸 Monitoring image area at ({x}, {y}) {width}x{height}")
                            
                    except ImportError:
                        self.element_processed.emit(f"⚠️ OpenCV not available. Please install: pip install opencv-python")
                    except Exception as e:
                        self.element_processed.emit(f"❌ Image monitoring failed: {str(e)}")
                    
                # Wait a bit
                time.sleep(1)
                
            self.status_updated.emit("Automation completed!")
            
        except Exception as e:
            self.status_updated.emit(f"Execution error: {str(e)}")
            
    def stop(self):
        """Stop execution"""
        self.running = False

class SmartAutomation(QMainWindow):
    """Smart Automation Assistant main interface"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🤖 Smart Automation Assistant")
        self.setMinimumSize(600, 500)
        self.elements = []
        self.automation_thread = None
        self.initUI()
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("🤖 Smart Automation Assistant")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px;
                background-color: #ecf0f1;
                border-radius: 10px;
                margin: 10px;
            }
        """)
        main_layout.addWidget(title)
        
        # Status display
        self.status_label = QLabel("Ready - Please add elements to automate")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
                margin: 5px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Add Element")
        self.add_btn.clicked.connect(self.add_element)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        self.start_btn = QPushButton("▶️ Start Automation")
        self.start_btn.clicked.connect(self.start_automation)
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        main_layout.addLayout(button_layout)
        
        # Element list
        list_label = QLabel("📋 Automation Elements List:")
        list_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        main_layout.addWidget(list_label)
        
        self.element_list = QListWidget()
        self.element_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
        """)
        main_layout.addWidget(self.element_list)
        
        # Log display
        log_label = QLabel("📝 Execution Log:")
        log_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        main_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                font-family: monospace;
            }
        """)
        main_layout.addWidget(self.log_text)
        
    def add_element(self):
        """Add element"""
        try:
            # Use the precise selector from original_precise_selector.py
            try:
                from original_precise_selector import OriginalPreciseSelector
                selector = OriginalPreciseSelector(self)
            except ImportError:
                # If precise selector is not available, use simple selector
                selector = ElementSelector(self)
                
            if selector.exec() == QDialog.Accepted and selector.selected_element:
                element = selector.selected_element
                self.elements.append(element)
                self.update_element_list()
                self.log_message(f"✅ Element added: {element['type']} position:({element['x']}, {element['y']})")
                
                # If there are elements, enable start button
                if len(self.elements) > 0:
                    self.start_btn.setEnabled(True)
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add element: {str(e)}")
            import traceback
            print(f"Error details: {traceback.format_exc()}")
            
    def update_element_list(self):
        """Update element list display"""
        self.element_list.clear()
        for i, element in enumerate(self.elements):
            item_text = f"{i+1}. {element['type']}"
            
            # Add position/area information
            if 'width' in element and 'height' in element:
                item_text += f" - Area: ({element['x']}, {element['y']}) {element['width']}x{element['height']}"
            else:
                item_text += f" - Position: ({element['x']}, {element['y']})"
            
            # Add parameter information
            if element['parameter']:
                item_text += f" - Param: {element['parameter']}"
                
            item = QListWidgetItem(item_text)
            self.element_list.addItem(item)
            
    def start_automation(self):
        """Start automation"""
        if not self.elements:
            QMessageBox.warning(self, "Warning", "Please add elements first!")
            return
            
        try:
            self.automation_thread = AutomationThread(self.elements)
            self.automation_thread.status_updated.connect(self.update_status)
            self.automation_thread.element_processed.connect(self.log_message)
            self.automation_thread.finished.connect(self.automation_finished)
            
            self.automation_thread.start()
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.add_btn.setEnabled(False)
            
            self.log_message("🚀 Starting automation...")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start automation: {str(e)}")
            
    def stop_automation(self):
        """Stop automation"""
        if self.automation_thread:
            self.automation_thread.stop()
            self.automation_thread.wait()
            
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.add_btn.setEnabled(True)
        
        self.log_message("⏹️ Automation stopped")
        
    def automation_finished(self):
        """Automation completed"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.add_btn.setEnabled(True)
        
    def update_status(self, status):
        """Update status"""
        self.status_label.setText(status)
        
    def log_message(self, message):
        """Add log message"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def closeEvent(self, event):
        """Close event"""
        if self.automation_thread and self.automation_thread.isRunning():
            self.automation_thread.stop()
            self.automation_thread.wait()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = SmartAutomation()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 