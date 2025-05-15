from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QFrame, QGridLayout,
                             QScrollArea, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal, QDateTime
from PySide6.QtGui import QPixmap
import cv2
import numpy as np
import pyautogui
import time
import os
from datetime import datetime

class RecognitionThread(QThread):
    calibration_progress = Signal(float, float)  # 進度百分比, 當前最佳比例
    calibration_complete = Signal(float)  # 最終最佳比例
    element_detected = Signal(str, tuple, float, tuple)  # 元件名稱, 位置, 置信度, 原始尺寸
    error_occurred = Signal(str)

    def __init__(self, template_paths, parent=None):
        super().__init__(parent)
        self.template_paths = template_paths
        self.templates = {}
        self.running = False
        self.best_scale = 1.0
        self.calibration_mode = True
        self._stop = False
        self.load_templates()
        
    def load_templates(self):
        """載入所有模板圖片"""
        try:
            for name, path in self.template_paths.items():
                template = cv2.imread(path)
                if template is not None:
                    self.templates[name] = {'image': template, 'size': template.shape[:2][::-1]}
                    print(f"成功載入模板 {name}, 尺寸: {template.shape[:2]}")
                else:
                    print(f"無法載入模板 {name}: {path}")
        except Exception as e:
            print(f"載入模板時發生錯誤: {str(e)}")

    def find_best_scale(self):
        """找出最佳縮放比例"""
        try:
            print("開始尋找最佳縮放比例...")
            best_scale = 1.0
            best_confidence = 0
            scale_range = np.arange(0.3, 1.51, 0.05)
            calibration_template = self.templates.get("Calibration_Frame", {}).get('image')

            if calibration_template is None:
                print("錯誤: 未找到校正匡模板")
                return 1.0

            start_time = time.time()
            while time.time() - start_time < 30:
                try:
                    screenshot = pyautogui.screenshot()
                    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    
                    for scale in scale_range:
                        if self._stop:
                            return best_scale
                            
                        print(f"測試縮放比例: {scale:.2f}")
                        resized_template = cv2.resize(calibration_template, (0, 0), 
                                                    fx=scale, fy=scale)
                        result = cv2.matchTemplate(frame, resized_template, 
                                                 cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, _ = cv2.minMaxLoc(result)
                        
                        if max_val > best_confidence:
                            best_confidence = max_val
                            best_scale = scale
                            print(f"找到更好的比例: {scale:.2f}, 置信度: {max_val:.3f}")
                    
                    progress = ((time.time() - start_time) / 30) * 100
                    self.calibration_progress.emit(progress, best_scale)
                    
                    if best_confidence > 0.9:
                        print(f"找到理想比例: {best_scale:.2f}, 置信度: {best_confidence:.3f}")
                        break
                        
                    time.sleep(0.5)
                
                except Exception as e:
                    print(f"縮放測試中發生錯誤: {str(e)}")
                    continue

            return best_scale
            
        except Exception as e:
            print(f"find_best_scale 方法發生錯誤: {str(e)}")
            return 1.0

    def run(self):
        try:
            self.running = True
            self._stop = False
            
            # 階段1：找最佳比例
            if self.calibration_mode:
                self.best_scale = self.find_best_scale()
                if self._stop:
                    return
                self.calibration_complete.emit(self.best_scale)
                print(f"完成比例校正: {self.best_scale}")
                
                with open("./templates/best_scale.txt", "w", encoding="utf-8") as file:
                    file.write(f"best_scale,{self.best_scale}\n")  # 格式：best_scale, <value>
                    print(f"已将最佳缩放比例 {self.best_scale} 保存到文件")
#-----------------------------------------------------------
                self.calibration_mode = False
                time.sleep(1)
            
            # 階段2：元件辨識
            detection_counts = {name: 0 for name in self.templates if name != "Calibration_Frame"}
            
            while self.running and not self._stop:
                try:
                    all_detected = all(count >= 3 for count in detection_counts.values())
                    if all_detected:
                        print("所有元件已完成辨識！")
                        break

                    screenshot = pyautogui.screenshot()
                    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

                    for element_name, template_info in self.templates.items():
                        if element_name != "Calibration_Frame" and detection_counts[element_name] < 3:
                            try:
                                template = template_info['image']
                                original_size = template_info['size']
                                resized_template = cv2.resize(template, (0, 0), 
                                                            fx=self.best_scale, 
                                                            fy=self.best_scale)
                                result = cv2.matchTemplate(frame, resized_template, 
                                                         cv2.TM_CCOEFF_NORMED)
                                _, confidence, _, position = cv2.minMaxLoc(result)
                                
                                if confidence > 0.8:
                                    scaled_size = tuple(int(s * self.best_scale) for s in original_size)
                                    print(f"成功檢測到 {element_name}!")
                                    print(f"- 置信度: {confidence:.3f}")
                                    print(f"- 位置: {position}")
                                    print(f"- 尺寸: {scaled_size}")
                                    self.element_detected.emit(element_name, position, 
                                                            confidence, scaled_size)
                                    detection_counts[element_name] += 1
                            except Exception as e:
                                print(f"處理 {element_name} 時發生錯誤: {str(e)}")

                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"辨識循環發生錯誤: {str(e)}")
                    continue
                
        except Exception as e:
            print(f"執行緒主循環發生錯誤: {str(e)}")
            self.error_occurred.emit(str(e))
        finally:
            print("辨識執行緒結束")
            self.running = False

    def stop(self):
        """停止辨識執行緒"""
        self._stop = True
        self.running = False
        self.wait()

class ElementDisplay(QFrame):
    """元件顯示框架"""
    def __init__(self, element_name, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setMinimumSize(250, 200)
        
        layout = QVBoxLayout(self)
        
        self.name_label = QLabel(element_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("font-weight: bold;")
        
        self.count_label = QLabel("辨識次數: 0/3")
        self.count_label.setAlignment(Qt.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setMinimumSize(220, 150)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0;")
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.count_label)
        layout.addWidget(self.image_label)

    def update_count(self, count):
        self.count_label.setText(f"辨識次數: {count}/3")

    def set_image(self, pixmap):
        if pixmap:
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

class CorrectionTool(QWidget):
    correction_finished = Signal(dict)

    def __init__(self, template_paths):
        super().__init__()
        self.setWindowTitle("元件校正工具")
        self.template_paths = template_paths
        self.temp_dir = "temp_calibration"
        self.ensure_temp_dir()
        
        self.detection_records = {
            "Big_Button": [], "Dual_Button": [], "Payout_In_Progress": [],
            "Stop_Betting": [], "Chip_Button": [], "Bet_Button": [], "Game_Result_Area": []
        }
        
        
        self.best_scale = 1.0
        self.initUI()

    def ensure_temp_dir(self):
        """確保暫存目錄存在"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def initUI(self):
        """初始化使用者介面"""
        main_layout = QVBoxLayout(self)
        
        # 上方狀態區
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        
        self.phase_label = QLabel("校正階段：尋找最佳縮放比例")
        self.phase_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        status_layout.addWidget(self.phase_label)
        
        self.progress_bar = QProgressBar()
        status_layout.addWidget(self.progress_bar)
        
        self.scale_label = QLabel("當前最佳比例: 1.0")
        status_layout.addWidget(self.scale_label)
        
        main_layout.addWidget(status_frame)
        
        # 元件顯示區
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        grid_layout = QGridLayout(scroll_widget)
        
        self.element_displays = {}
        row = 0
        col = 0
        for element_name in self.detection_records.keys():
            display = ElementDisplay(element_name)
            self.element_displays[element_name] = display
            grid_layout.addWidget(display, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # 底部控制區
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        
        self.start_btn = QPushButton("開始校正")
        self.start_btn.clicked.connect(self.start_correction)
        
        self.confirm_btn = QPushButton("確認校正結果")
        self.confirm_btn.clicked.connect(self.confirm_correction)
        self.confirm_btn.setEnabled(False)
        
        self.recalibrate_btn = QPushButton("重新校正")
        self.recalibrate_btn.clicked.connect(self.start_correction)
        self.recalibrate_btn.setEnabled(False)
        
        for btn in [self.start_btn, self.confirm_btn, self.recalibrate_btn]:
            btn.setMinimumWidth(120)
            control_layout.addWidget(btn)
        
        main_layout.addWidget(control_frame)

    def start_correction(self):
        """開始校正流程"""
        self.cleanup_temp_files()
        self.detection_records = {k: [] for k in self.detection_records}
        for display in self.element_displays.values():
            display.update_count(0)
            display.image_label.clear()
        
        self.start_btn.setEnabled(False)
        self.confirm_btn.setEnabled(False)
        self.recalibrate_btn.setEnabled(False)
        
        self.recognition_thread = RecognitionThread(self.template_paths, self)
        self.recognition_thread.calibration_progress.connect(self.update_progress)
        self.recognition_thread.calibration_complete.connect(self.on_calibration_complete)
        self.recognition_thread.element_detected.connect(self.on_element_detected)
        self.recognition_thread.error_occurred.connect(self.handle_error)
        
        self.recognition_thread.start()

    def update_progress(self, progress, current_scale):
        """更新進度條和比例顯示"""
        self.progress_bar.setValue(int(progress))
        self.scale_label.setText(f"當前最佳比例: {current_scale:.2f}")

    def on_calibration_complete(self, best_scale):
        """校正完成處理"""
        self.best_scale = best_scale
        self.phase_label.setText("校正階段：驗證元件辨識位置")
        self.recalibrate_btn.setEnabled(True)

    def on_element_detected(self, element_name, position, confidence, size):
        """處理元件檢測結果"""
        if element_name in self.detection_records:
            self.detection_records[element_name].append({
                'position': position,
                'confidence': confidence,
                'size': size,
                'time': datetime.now()
            })
            
            count = len(self.detection_records[element_name])
            self.element_displays[element_name].update_count(count)
            
            if count == 3:
                self.generate_element_image(element_name)
            
            if self.check_all_complete():
                self.confirm_btn.setEnabled(True)

    def generate_element_image(self, element_name):
        """生成元件辨識結果圖片"""
        try:
            screenshot = pyautogui.screenshot()
            image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 計算所有檢測框的範圍
            padding = 20  # 邊界寬度
            min_x = min_y = float('inf')
            max_x = max_y = 0
            
            for record in self.detection_records[element_name]:
                pos = record['position']
                size = record['size']
                min_x = min(min_x, pos[0] - padding)
                min_y = min(min_y, pos[1] - padding)
                max_x = max(max_x, pos[0] + size[0] + padding)
                max_y = max(max_y, pos[1] + size[1] + padding)
            
            # 確保範圍在合理區間內
            height, width = image.shape[:2]
            min_x = max(0, int(min_x))
            min_y = max(0, int(min_y))
            max_x = min(width, int(max_x))
            max_y = min(height, int(max_y))
            
            # 裁切圖片
            cropped_image = image[min_y:max_y, min_x:max_x]
            
            # 在裁切後的圖片上繪製框線
            for record in self.detection_records[element_name]:
                pos = record['position']
                size = record['size']
                confidence = record['confidence']
                
                # 調整位置到裁切後的坐標系
                adjusted_pos = (pos[0] - min_x, pos[1] - min_y)
                
                # 畫框
                cv2.rectangle(
                    cropped_image,
                    adjusted_pos,
                    (adjusted_pos[0] + size[0], adjusted_pos[1] + size[1]),
                    (0, 255, 0),
                    2
                )
                
                # 添加文字
                cv2.putText(
                    cropped_image,
                    f"{confidence:.2f}",
                    (adjusted_pos[0], adjusted_pos[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )
            
            # 保存裁切後的圖片
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.temp_dir}/{element_name}_{timestamp}.png"
            cv2.imwrite(filename, cropped_image)
            print(f"已保存圖片: {filename}")
            
            # 更新UI顯示
            self.element_displays[element_name].set_image(QPixmap(filename))
            
        except Exception as e:
            print(f"生成圖片時發生錯誤: {str(e)}")
            self.handle_error(f"生成圖片時發生錯誤: {str(e)}")

    def check_all_complete(self):
        """檢查是否所有元件都完成辨識"""
        for name, records in self.detection_records.items():
            print(f"檢查 {name}: {len(records)}/3")
        return all(len(records) >= 3 for records in self.detection_records.values())
        
    def confirm_correction(self):
        print("確認校正結果並儲存位置信息...")
        try:
            if hasattr(self, 'recognition_thread'):
                self.recognition_thread.stop()
        
            # 計算並儲存中心點位置
            positions_file = os.path.join("templates", "positions.txt")
            with open(positions_file, 'w', encoding='utf-8') as f:
                for element_name, records in self.detection_records.items():
                    if records:  # 確保有檢測記錄
                        # 取最後一次的檢測結果
                        last_record = records[-1]
                        pos = last_record['position']
                        size = last_record['size']
                        
                        if element_name == "Game_Result_Area":
                            # 儲存完整區域資訊
                            f.write(f"{element_name},{pos[0]},{pos[1]},{size[0]},{size[1]}\n")
                            print(f"已儲存 {element_name} 的位置信息: ({center_x}, {center_y})")
                        else:
                            # 計算中心點
                            center_x = pos[0] + size[0] // 2
                            center_y = pos[1] + size[1] // 2
                    
                            # 寫入檔案
                            f.write(f"{element_name},{center_x},{center_y}\n")
                            print(f"已儲存 {element_name} 的位置信息: ({center_x}, {center_y})")
        
            print("位置信息儲存完成")
        
            result = {
                "scale": self.best_scale,
                "records": self.detection_records
            }
            self.correction_finished.emit(result)
        
        except Exception as e:
            print(f"儲存位置信息時發生錯誤: {str(e)}")
            self.handle_error(f"儲存位置信息時發生錯誤: {str(e)}")
            
    def handle_error(self, error_msg):
        """處理錯誤"""
        print(f"錯誤: {error_msg}")
        QMessageBox.warning(self, "校正錯誤", error_msg)

    def cleanup_temp_files(self):
        """清理暫存檔案"""
        try:
            print("清理暫存檔案...")
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        print(f"已刪除: {file_path}")
                    except Exception as e:
                        print(f"刪除檔案 {file_path} 時發生錯誤: {str(e)}")
        except Exception as e:
            print(f"清理暫存檔案時發生錯誤: {str(e)}")

    def closeEvent(self, event):
        """關閉視窗時的處理"""
        print("關閉校正工具...")
        if hasattr(self, 'recognition_thread'):
            self.recognition_thread.stop()
        self.cleanup_temp_files()
        super().closeEvent(event)
        