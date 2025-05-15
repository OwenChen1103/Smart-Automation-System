from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QPushButton, QLabel, QFrame, QVBoxLayout, QFileDialog,
                             QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from Correction_Tool import CorrectionTool

import cv2
import numpy as np
import sys
import os
import shutil

class CaptureBlock(QFrame):
    """圖片匯入區塊元件"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setMinimumSize(200, 200)
        self.captured = False
        
        self.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold;")
        
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setText("未匯入圖片")
        self.preview.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #ddd;
                padding: 5px;
            }
        """)
        self.preview.setMinimumSize(180, 120)
        
        self.capture_btn = QPushButton("選擇圖片")
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.preview)
        layout.addWidget(self.capture_btn)
        
    def set_captured_image(self, pixmap):
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview.setPixmap(scaled_pixmap)
            self.captured = True
            self.setStyleSheet("""
                QFrame {
                    background-color: #f5f5f5;
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                }
            """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("圖像匯入與校正工具")
        self.setMinimumSize(800, 600)
        
        # 確保存放模板的目錄存在
        self.template_dir = "templates"
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        grid_layout = QGridLayout()
        
        # 進度標籤
        self.progress_label = QLabel("進度: 0/7")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 10px;
            }
        """)
        main_layout.addWidget(self.progress_label)
        
        # 素材標題列表
        self.materials = [
            "Calibration_Frame", "Big_Button", "Dual_Button", "Payout_In_Progress",
            "Stop_Betting", "Chip_Button", "Bet_Button", "Game_Result_Area"
        ]
        
        # 建立擷取區塊
        self.capture_blocks = []
        for i, title in enumerate(self.materials):
            block = CaptureBlock(title)
            block.capture_btn.clicked.connect(lambda checked, index=i: self.import_image(index))
            grid_layout.addWidget(block, i // 4, i % 4)
            self.capture_blocks.append(block)
        
        main_layout.addLayout(grid_layout)
        
        # 完成按鈕
        self.complete_btn = QPushButton("開始校正")
        self.complete_btn.setEnabled(False)
        self.complete_btn.clicked.connect(self.start_correction)
        self.complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        main_layout.addWidget(self.complete_btn, alignment=Qt.AlignCenter)
    
    def import_image(self, block_index):
        """匯入圖片"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "選擇圖片",
            "",
            "圖片檔案 (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_name:
            try:
                # 複製圖片到templates目錄
                target_filename = f"{self.materials[block_index]}.png"
                target_path = os.path.join(self.template_dir, target_filename)
                
                # 複製檔案
                shutil.copy2(file_name, target_path)
                print(f"已將圖片複製至: {target_path}")
                
                # 更新UI顯示
                pixmap = QPixmap(file_name)
                if not pixmap.isNull():
                    self.capture_blocks[block_index].set_captured_image(pixmap)
                    self.update_progress()
                else:
                    raise Exception("無法載入圖片")
                    
            except Exception as e:
                QMessageBox.warning(self, "錯誤", f"匯入圖片時發生錯誤: {str(e)}")
                # 如果發生錯誤，刪除可能已複製的檔案
                if os.path.exists(target_path):
                    os.remove(target_path)
    
    def update_progress(self):
        """更新進度"""
        captured_count = sum(1 for block in self.capture_blocks if block.captured)
        self.progress_label.setText(f"進度: {captured_count}/{len(self.materials)}")
        self.complete_btn.setEnabled(captured_count == len(self.materials))
    
    def start_correction(self):
        """開始校正流程"""
        # 收集所有模板的路徑
        template_paths = {}
        for block in self.capture_blocks:
            if block.captured:
                template_name = block.title_label.text()
                template_path = os.path.join(self.template_dir, f"{template_name}.png")
                template_paths[template_name] = template_path
                print(f"載入模板: {template_name} -> {template_path}")
        
        # 創建並顯示校正工具
        self.correction_tool = CorrectionTool(template_paths)
        self.correction_tool.correction_finished.connect(self.handle_correction_complete)
        self.correction_tool.show()
        self.hide()
    
    def handle_correction_complete(self, result):
        """處理校正完成後的結果"""
        self.best_scale = result["scale"]
        self.calibration_records = result["records"]
        print(f"校正完成，最佳比例: {self.best_scale}")
        
        self.show()
        self.correction_tool.close()
        
        # 開啟結果視窗
        from ResultWindow import ResultWindow
        self.result_window = ResultWindow()
        self.result_window.show()
        self.close()

    def closeEvent(self, event):
        """關閉視窗時的處理"""
        print("關閉主視窗...")
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())