#!/usr/bin/env python3
"""
Original Precise Element Selector (Fixed Version)
Based on the original design, only fixing necessary text display issues
"""

import os
import sys
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QDialog, 
                             QComboBox, QLineEdit, QMessageBox, QSpinBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
import pyautogui

class OriginalPreciseSelector(QDialog):
    """Original Precise Element Selector"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Precise Element Selector")
        self.setFixedSize(500, 400)
        self.selected_element = None
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🎯 Precise Element Selector")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Instructions
        instruction = QLabel("Please select the element type and precise position to automate:")
        instruction.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(instruction)
        
        # Element type selection
        type_label = QLabel("Element Type:")
        type_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(type_label)
        
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
        param_label = QLabel("Parameter Settings:")
        param_label.setStyleSheet("font-weight: bold; padding-top: 10px;")
        layout.addWidget(param_label)
        
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
        
        # Coordinate input
        coord_label = QLabel("Precise Coordinates (Optional):")
        coord_label.setStyleSheet("font-weight: bold; padding-top: 10px;")
        layout.addWidget(coord_label)
        
        coord_layout = QHBoxLayout()
        
        coord_layout.addWidget(QLabel("X:"))
        self.x_coord = QSpinBox()
        self.x_coord.setRange(0, 9999)
        self.x_coord.setValue(0)
        self.x_coord.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px;")
        coord_layout.addWidget(self.x_coord)
        
        coord_layout.addWidget(QLabel("Y:"))
        self.y_coord = QSpinBox()
        self.y_coord.setRange(0, 9999)
        self.y_coord.setValue(0)
        self.y_coord.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px;")
        coord_layout.addWidget(self.y_coord)
        
        layout.addLayout(coord_layout)
        
        # Current mouse position display
        self.mouse_pos_label = QLabel("Current mouse position: Not obtained")
        self.mouse_pos_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-family: monospace;
                color: #333333;
            }
        """)
        layout.addWidget(self.mouse_pos_label)
        
        # Enter key hint
        enter_hint = QLabel("💡 Tip: Move mouse to target position, then press Enter to get coordinates")
        enter_hint.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #e8f4fd;
                border: 1px solid #bee5eb;
                border-radius: 5px;
                color: #0c5460;
                font-size: 12px;
            }
        """)
        layout.addWidget(enter_hint)
        
        # Button area
        button_layout = QHBoxLayout()
        
        self.get_pos_btn = QPushButton("📍 Get Current Position")
        self.get_pos_btn.clicked.connect(self.get_current_position)
        self.get_pos_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        
        self.select_btn = QPushButton("🎯 Select Element")
        self.select_btn.clicked.connect(self.select_element)
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
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
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addWidget(self.get_pos_btn)
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Update parameter hints
        self.element_type.currentTextChanged.connect(self.update_param_hint)
        self.update_param_hint()
        
        # Timer to update mouse position
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_mouse_position)
        self.timer.start(100)  # Update every 100ms
        
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
            
    def update_mouse_position(self):
        """Update mouse position display"""
        try:
            x, y = pyautogui.position()
            self.mouse_pos_label.setText(f"Current mouse position: ({x}, {y})")
        except:
            pass
            
    def get_current_position(self):
        """Get current mouse position"""
        try:
            x, y = pyautogui.position()
            self.x_coord.setValue(x)
            self.y_coord.setValue(y)
            self.mouse_pos_label.setText(f"Position obtained: ({x}, {y})")
            self.mouse_pos_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 5px;
                    font-family: monospace;
                    color: #155724;
                }
            """)
            QMessageBox.information(self, "Position Obtained", f"Mouse position obtained: ({x}, {y})")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get position: {str(e)}")
            
    def select_element(self):
        """Select element"""
        try:
            current_type = self.element_type.currentText()
            
            if "Monitor Text" in current_type or "Monitor Image" in current_type:
                # For monitoring elements, we need area selection
                QMessageBox.information(self, "Area Selection Required", 
                    "For monitoring elements, you need to select a rectangular area.\n\n"
                    "Please use the main automation system to select monitoring areas.\n\n"
                    "This precise selector is best for single-point operations like clicking and text input.")
                self.reject()
                return
            
            # Check if coordinates are set
            x = self.x_coord.value()
            y = self.y_coord.value()
            
            if x == 0 and y == 0:
                # If no coordinates set, use current mouse position
                x, y = pyautogui.position()
                self.x_coord.setValue(x)
                self.y_coord.setValue(y)
            
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

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = OriginalPreciseSelector()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 