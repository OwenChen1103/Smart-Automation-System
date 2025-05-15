from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFrame, QGridLayout,
    QMessageBox, QCheckBox, QTableWidget, QTableWidgetItem, 
    QHeaderView, QProgressBar,QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QDateTime
from PySide6.QtGui import QPixmap, QColor, QFont
import sys
import cv2
import numpy as np
import pyautogui
import time
import os
from datetime import datetime
from BettingOperation import BettingOperation
from BettingLogger import BettingLogger

class MonitorThread(QThread):
    state_changed = Signal(dict)      # 發送狀態字典
    hand_counted = Signal(dict)       # 手數計數，包含更多詳細資訊
    result_captured = Signal(dict)    # 捕獲每手牌結果
    game_result_detected = Signal(dict)  # 新增：遊戲結果信號


    def __init__(self, positions, parent=None):
        super().__init__(parent)
        self.positions = positions
        self.running = False
        self.hand_count = 0
        self._stop = False
        self.templates = {}
        self.best_scale = 1.0
        self.last_result = None  # 新增：記錄上一次的結果
        self.last_result_time = None  # 新增：記錄上一次結果的時間
        self.current_round_results = []  # 存儲結果
        self.previous_hand_info = None  # 新增：儲存上一手牌的資訊
        self.previous_state = None  # 新增：儲存上一個狀態
        self.betting_operation = None  # 初始化为 None


        
        # 載入模板
        self.load_templates()
    
    def set_betting_operation(self, betting_op):
        """设置 betting operation 引用"""
        self.betting_operation = betting_op

    def load_templates(self):
        """載入所有模板圖片"""
        try:
            # 首先讀取全局 best_scale
            scale_path = os.path.join('./templates', 'best_scale.txt')
            try:
                with open(scale_path, 'r') as f:
                    content = f.read().strip()
                    best_scale_str = content.split(',')[-1].strip()
                    self.best_scale = float(best_scale_str)
            except (FileNotFoundError, ValueError) as e:
                print(f"讀取 best_scale 時出錯: {e}")
                self.best_scale = 1.0  # 預設值

            # 載入模板
            template_files = [f for f in os.listdir('./templates') if f.endswith('.png')]
            
            for template_file in template_files:
                name = os.path.splitext(template_file)[0]
                full_path = os.path.join('./templates', template_file)
                template = cv2.imread(full_path)
                
                if template is not None:
                    self.templates[name] = {
                        'image': template, 
                        'size': template.shape[:2][::-1]
                    }
                    print(f"成功載入模板 {name}, 尺寸: {template.shape[:2]}")
                else:
                    print(f"無法載入模板 {name}")
        except Exception as e:
            print(f"載入模板時發生錯誤: {str(e)}")

    def run(self):
        last_state = None
        self.running = True
        self._stop = False
        self.hand_count = 0

        while not self._stop:
            try:
                # 截取螢幕
                screenshot = pyautogui.screenshot()
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # 檢查各狀態
                current_state = {
                    'betting_time': self.check_betting_state(frame),
                    'paying': self.check_paying_state(frame),
                    'stop_betting': self.check_stop_betting(frame)
                }
                
                # 持續監測遊戲結果
                current_result = self.check_game_result(frame)
                current_time = time.time()
                
                # 如果檢測到新的結果且與上一次不同
                if (current_result is not None and 
                    (self.last_result != current_result or 
                     self.last_result_time is None or 
                     current_time - self.last_result_time > 5)):  # 5秒防抖動
                    
                    self.last_result = current_result
                    self.last_result_time = current_time
                    
                    # 發送結果信號
                    result_data = {
                        'game_result': current_result,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    }
                    self.game_result_detected.emit(result_data)
                    
                # 檢測從非下注時間變為下注時間的狀態轉換
                if (self.previous_state is not None and 
                    not self.previous_state['betting_time'] and 
                    current_state['betting_time']):
                
                    # 此時記錄上一手牌的資訊
                    if (self.previous_hand_info is not None and 
                        hasattr(self, 'betting_operation') and 
                        (self.betting_operation.running or 
                        getattr(self.betting_operation, 'waiting_for_final_record', False))):
                        
                         
                        result = {
                            'hand_number': self.previous_hand_info['hand_number'],
                            'bet_type': self.previous_hand_info['bet_type'],
                            'bet_size': self.previous_hand_info['bet_size'],
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'status': '完成',
                            'details': self.previous_hand_info['details'],
                            'game_result': self.last_result
                        }
                        self.result_captured.emit(result)
                        
                        # 如果是在等待最後記錄，現在可以完全停止了
                        if getattr(self.betting_operation, 'waiting_for_final_record', False):
                            self.betting_operation.waiting_for_final_record = False
                            print("最後一手結果已記錄完成")
                        
                # 狀態改變時發送信號
                if current_state != last_state:
                    self.state_changed.emit(current_state)
                    last_state = current_state.copy()
            
                # 更新上一個狀態
                self.previous_state = current_state.copy()
            
                                
                          
                
                
                
                time.sleep(0.3)
            
            except Exception as e:
                print(f"監控執行緒錯誤: {str(e)}")
                time.sleep(1)

    def check_betting_state(self, frame):
        return self._check_template_match(frame, 'Payout_In_Progress')

    def check_paying_state(self, frame):
        return self._check_template_match(frame, 'Payout_In_Progress')

    def check_stop_betting(self, frame):
        return self._check_template_match(frame, 'Stop_Betting')

    def _check_template_match(self, frame, template_key, threshold=0.8):
        try:
            template_info = self.templates.get(template_key)
            if not template_info:
                print(f"未找到模板: {template_key}")
                return False
            
            template = template_info['image']
            resized_template = cv2.resize(template, (0, 0), 
                                        fx=self.best_scale, 
                                        fy=self.best_scale)
            
            result = cv2.matchTemplate(frame, resized_template, cv2.TM_CCOEFF_NORMED)
            _, confidence, _, _ = cv2.minMaxLoc(result)
            
            return confidence > threshold
        except Exception as e:
            print(f"檢查 {template_key} 狀態時發生錯誤: {str(e)}")
            return False

    def record_hand_result(self, result):
        """記錄每手的結果"""
        if result:
            # 添加遊戲結果到結果字典
            if self.last_result is not None:
                result['game_result'] = self.last_result
            
            # 發送結果信號
            self.result_captured.emit(result)
            self.hand_count += 1

            # 發送單手結果信號
            hand_info = {
                'hand_number': self.hand_count,
                'round_number': (self.hand_count - 1) // 50 + 1,
                'hand_in_round': (self.hand_count - 1) % 50 + 1
            }
            self.hand_counted.emit(hand_info)

    def check_game_result(self, frame):
        """
        檢查遊戲結果
        回傳：結果代號(0-4)或 None
        """
        try:
            # 取得 Game_Result_Area 的位置
            result_area = self.positions.get("Game_Result_Area")
            if not result_area:
                return None
                
            # 裁切結果區域
            area_image = frame[
                result_area['y']:result_area['y']+result_area['height'],
                result_area['x']:result_area['x']+result_area['width']
            ]
            
            # 檢查每個可能的結果
            highest_confidence = 0
            detected_result = None
            
            for i in range(5):
                template = self.templates.get(f'result_{i}')
                if template:
                    result = cv2.matchTemplate(
                        area_image, 
                        cv2.resize(template['image'], (0, 0), 
                                 fx=self.best_scale, 
                                 fy=self.best_scale),
                        cv2.TM_CCOEFF_NORMED
                    )
                    _, confidence, _, _ = cv2.minMaxLoc(result)
                    
                    if confidence > 0.8 and confidence > highest_confidence:
                        highest_confidence = confidence
                        detected_result = i
            
            return detected_result
                
        except Exception as e:
            print(f"檢查遊戲結果時發生錯誤: {str(e)}")
            return None

    def stop(self):
        """停止執行緒"""
        self._stop = True
        self.running = False
        self.wait()

class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # 設置視窗基本屬性
        self.setWindowTitle("色諜監控面板")
        self.setMinimumSize(400, 400)
        # 設置視窗標誌
        flags = self.windowFlags()
        self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)  # 固定在最上層
        
        # 允許調整大小
        self.setSizePolicy(
            QSizePolicy.Expanding,    # 水平方向可以擴展
            QSizePolicy.Expanding     # 垂直方向可以擴展
        )
        
        self.setStyleSheet("""
            QWidget { background-color: #f0f0f0; }
            QFrame { 
                background-color: white; 
                border: 1px solid #d0d0d0; 
                border-radius: 5px; 
            }
            QLabel { 
                font-size: 14px; 
                color: #333; 
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLabel#status_label {
                font-weight: bold;
                font-size: 16px;
                padding: 5px;
                border-radius: 5px;
            }
            QLabel#betting_status {
                background-color: #FFD700;
                color: black;
            }
            QLabel#paying_status {
                background-color: #98FB98;
                color: black;
            }
            QLabel#stop_betting_status {
                background-color: #FF6347;
                color: white;
            }
        """)
        
        # 載入位置資訊
        self.load_positions()
        
        # 初始化變數
        self.betting_op = None
        self.current_hand = 0
        self.result_images = []
        
        # 初始化UI
        self.initUI()
        
        # 初始化記錄器
        self.logger = BettingLogger()
        
        # 初始化監控執行緒
        self.monitor_thread = MonitorThread(self.positions, self)
        self.monitor_thread.state_changed.connect(self.update_state)
        self.monitor_thread.hand_counted.connect(self.update_hand_count)
        self.monitor_thread.result_captured.connect(self.update_hand_result)
        self.monitor_thread.game_result_detected.connect(self.handle_game_result) 
        
        # 啟動監控
        self.monitor_thread.start()

    def load_positions(self):
        """載入位置資訊"""
        self.positions = {}
        try:
            with open(os.path.join("templates", "positions.txt"), 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if parts[0] == "Game_Result_Area":
                        self.positions[parts[0]] = {
                            'x': int(parts[1]),
                            'y': int(parts[2]),
                            'width': int(parts[3]),
                            'height': int(parts[4])
                        }
                    else:
                        self.positions[parts[0]] = {
                            'x': int(parts[1]),
                            'y': int(parts[2])
                        }
            print("成功載入位置資訊")
        except Exception as e:
            print(f"載入位置資訊時發生錯誤: {str(e)}")
            QMessageBox.warning(self, "錯誤", "無法載入位置資訊，請先進行校正。")

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # 狀態顯示區域
        status_frame = QFrame()
        status_layout = QGridLayout(status_frame)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
                margin: 0.5px;
            }
        """)
        status_layout.addWidget(QLabel("遊戲進度:"), 0, 0)
        status_layout.addWidget(self.progress_bar, 0, 1, 1, 3)
        
        # 狀態標籤
        self.betting_state_label = QLabel("下注狀態: 等待開始")
        self.betting_state_label.setObjectName("status_label")
        self.betting_state_label.setObjectName("betting_status")
        
        self.paying_state_label = QLabel("派彩狀態: 否")
        self.paying_state_label.setObjectName("status_label")
        self.paying_state_label.setObjectName("paying_status")
        
        self.stop_betting_label = QLabel("停止下注: 否")
        self.stop_betting_label.setObjectName("status_label")
        self.stop_betting_label.setObjectName("stop_betting_status")
        
        # 新增開牌結果標籤
        self.game_result_label = QLabel("開牌結果: 等待開牌")
        self.game_result_label.setObjectName("status_label")
        self.game_result_label.setStyleSheet("""
            QLabel {
                background-color: #4A90E2;
                color: white;
                padding: 5px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        status_layout.addWidget(self.betting_state_label, 1, 0, 1, 2)
        status_layout.addWidget(self.paying_state_label, 1, 2)
        status_layout.addWidget(self.stop_betting_label, 1, 3)
        status_layout.addWidget(self.game_result_label, 1, 4)
        
        main_layout.addWidget(status_frame)
        
        # 設定區域
        settings_frame = QFrame()
        settings_layout = QGridLayout(settings_frame)
        
        # 目標盤數
        settings_layout.addWidget(QLabel("目標盤數:"), 0, 0)
        self.target_rounds_input = QLineEdit()
        settings_layout.addWidget(self.target_rounds_input, 0, 1)
        
        # 下注尺寸
        settings_layout.addWidget(QLabel("下注尺寸(依籌碼面額為單位):"), 1, 0)
        self.bet_size_input = QLineEdit()
        settings_layout.addWidget(self.bet_size_input, 1, 1)
        
        # 下注選擇
        self.bet_big_checkbox = QCheckBox("下大")
        self.bet_double_checkbox = QCheckBox("下雙")
        settings_layout.addWidget(self.bet_big_checkbox, 2, 0)
        settings_layout.addWidget(self.bet_double_checkbox, 2, 1)
        
        main_layout.addWidget(settings_frame)
        
        # 結果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["手數", "結果", "詳情", "時間"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 設置表格樣式
        self.result_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #d0d0d0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        
        main_layout.addWidget(self.result_table)
        
        # 控制按鈕
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("開始下注")
        self.start_btn.clicked.connect(self.start_betting)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_betting)
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        main_layout.addLayout(control_layout)

    def update_state(self, state):
        """更新狀態顯示"""
        # 下注狀態
        betting_text = '下注時間' if state['betting_time'] else '非下注時間'
        self.betting_state_label.setText(f"下注狀態: {betting_text}")
        self.betting_state_label.setStyleSheet(
            "background-color: #98FB98;" if state['betting_time'] else "background-color: #FF6347; color: white;"
        )
        
        # 派彩狀態
        paying_text = '是' if state['paying'] else '否'
        self.paying_state_label.setText(f"派彩狀態: {paying_text}")
        self.paying_state_label.setStyleSheet(
            "background-color: #98FB98;" if state['paying'] else "background-color: #FFD700;"
        )
        
        # 停止下注狀態
        stop_betting_text = '是' if state['stop_betting'] else '否'
        self.stop_betting_label.setText(f"停止下注: {stop_betting_text}")
        self.stop_betting_label.setStyleSheet(
            "background-color: #FF6347; color: white;" if state['stop_betting'] else "background-color: #FFD700;"
        )
        
        # 如果在執行下注操作，傳遞狀態
        if self.betting_op and self.betting_op.running:
            self.betting_op.execute_betting(state)
            
    def handle_game_result(self, result_data):
        """處理遊戲結果"""
        self.current_game_result = result_data['game_result']
    
        # 更新結果標籤
        result_text = f"開牌結果: {self.current_game_result}"
        self.game_result_label.setText(result_text)
    
        # 根據不同結果設置不同的背景顏色
        colors = {
            0: "#FF6B6B",  # 紅色
            1: "#4ECDC4",  # 青色
            2: "#45B7D1",  # 藍色
            3: "#96CEB4",  # 綠色
            4: "#FFEEAD"   # 黃色
        }
    
        self.game_result_label.setStyleSheet(f"""
            QLabel {{
                background-color: {colors.get(self.current_game_result, '#4A90E2')};
                color: white;
                padding: 5px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)

    def update_hand_count(self, hand_info):
        """更新手數顯示"""
        if self.betting_op:
            # 設定最大值為目標盤數*50手
            max_hands = self.betting_op.target_rounds * 50
            
            # 更新進度條
            self.progress_bar.setMaximum(max_hands)
            self.progress_bar.setValue(hand_info['hand_number'])
        
            # 顯示詳細進度
            progress_text = (
                f"{hand_info['round_number']}盤 "
                f"{hand_info['hand_in_round']}手 "
                f"(共{hand_info['hand_number']}手)"
            )
            self.progress_bar.setFormat(progress_text)

    def update_hand_result(self, result):
        """更新手牌結果"""
        # 記錄到本地檔案
        self.logger.log_result(result)
        
        # 原有的表格更新代碼...
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        
        # 手數
        hand_item = QTableWidgetItem(str(result.get('hand_number', '')))
        hand_item.setTextAlignment(Qt.AlignCenter)
        self.result_table.setItem(row, 0, hand_item)

        # 結果（下注類型 + 下注尺寸）
        bet_info = f"{result.get('bet_type', '')} - {result.get('bet_size', '')}個籌碼尺寸"
        result_item = QTableWidgetItem(bet_info)
        result_item.setTextAlignment(Qt.AlignCenter)
        self.result_table.setItem(row, 1, result_item)

        # 詳情
        if result.get('result_image_path'):
            preview_btn = QPushButton("預覽結果")
            preview_btn.clicked.connect(lambda: self.show_result_image(result['result_image_path']))
            self.result_table.setCellWidget(row, 2, preview_btn)
        else:
            details_item = QTableWidgetItem(result.get('details', '成功下注'))
            details_item.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 2, details_item)

        # 時間
        time_item = QTableWidgetItem(result.get('timestamp', ''))
        time_item.setTextAlignment(Qt.AlignCenter)
        self.result_table.setItem(row, 3, time_item)

        # 自動滾動到最新行
        self.result_table.scrollToBottom()

        # 設置行高
        self.result_table.setRowHeight(row, 30)

        # 根據狀態設置行的背景顏色
        if result.get('status') == '成功下注':
            for col in range(4):
                item = self.result_table.item(row, col)
                if item:
                    item.setBackground(QColor('#E8F5E9'))  # 淺綠色背景

    def show_result_image(self, image_path):
        """顯示結果圖片"""
        preview_window = QWidget()
        preview_window.setWindowTitle("結果預覽")
        layout = QVBoxLayout()
        
        label = QLabel()
        pixmap = QPixmap(image_path)
        label.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        layout.addWidget(label)
        preview_window.setLayout(layout)
        preview_window.show()

    def start_betting(self):
        """開始下注"""
        try:
            # 驗證輸入
            target_rounds = int(self.target_rounds_input.text())
            bet_size = int(self.bet_size_input.text())

            if not (self.bet_big_checkbox.isChecked() or 
                   self.bet_double_checkbox.isChecked()):
                QMessageBox.warning(self, "錯誤", "請至少選擇一個下注選項")
                return
            
            # 開始新的記錄檔案
            self.logger = BettingLogger()

            # 建立下注操作實例
            self.betting_op = BettingOperation(
                positions=self.positions,
                bet_size=bet_size,
                target_rounds=target_rounds,
                bet_big=self.bet_big_checkbox.isChecked(),
                bet_double=self.bet_double_checkbox.isChecked()
            )
            
            # 设置 monitor_thread
            self.betting_op.monitor_thread = self.monitor_thread
            self.monitor_thread.set_betting_operation(self.betting_op)  # 在这里设置引用
        
        
            # 連接進度更新信號
            self.betting_op.progress_updated.connect(self.update_betting_progress)
        
            # 開始下注
            self.betting_op.start_betting()
        
            # 更新按鈕狀態
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        
        except ValueError:
            QMessageBox.warning(self, "錯誤", "請輸入有效的數字")

    def update_betting_progress(self, progress):
        """更新下注進度"""
        max_hands = progress['target_rounds'] * 50
    
        # 更新進度條
        self.progress_bar.setMaximum(max_hands)
        self.progress_bar.setValue(progress['current_hand'])
    
        # 顯示詳細進度
        progress_text = (
            f"{progress['current_round']}盤 "
            f"{progress['current_hand'] % 50}手 "
            f"(共{progress['current_hand']}手)"
        )
        self.progress_bar.setFormat(progress_text)
    
        # 如果達到目標盤數，自動停止
        if progress['is_completed']:
            self.stop_betting()

    def stop_betting(self):
        """停止下注"""
        if self.betting_op:
            self.betting_op.stop_betting()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def closeEvent(self, event):
        """關閉視窗時的處理"""
        self.monitor_thread.stop()
        if self.betting_op:
            self.betting_op.stop_betting()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = ResultWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()