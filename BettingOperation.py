import datetime
import pyautogui
import time
import random

from PySide6.QtCore import QObject, Signal

class BettingOperation(QObject):
    progress_updated = Signal(dict)  # 新增進度信號

    def __init__(self, positions, bet_size, target_rounds, bet_big=False, bet_double=False):
        super().__init__()
        self.positions = positions
        self.bet_size = bet_size
        self.target_rounds = target_rounds
        self.bet_big = bet_big
        self.bet_double = bet_double
        self.waiting_for_final_record = False  # 新增：等待最後記錄的標記

        
        # 重置遊戲進度相關變數
        self.current_hand = 0
        self.current_round = 0
        self.running = False

    def execute_betting(self, current_state):
        try:
            # 如果不在運行狀態，直接返回
            if not self.running:
                return False

            # 檢查是否在下注時間
            if current_state.get('betting_time', False):
            
                #8秒的值平分給4個隨機數
                remaining_seconds = 8.0
                time_values = []
    
                # 為前3個值隨機分配時間
                for i in range(3):
                    # 隨機分配剩餘時間的一部分
                    max_value = remaining_seconds - (3 - i) * 0.1  # 確保每個值至少分配到0.1秒
                    if max_value <= 0:
                            value = 0.1
                    else:
                        value = round(random.uniform(0.1, max_value), 1)
                    time_values.append(value)
                    remaining_seconds -= value
    
                # 最後一個值分配剩餘的時間
                time_values.append(round(remaining_seconds, 1))
                
                
                
                
                
                # 點擊籌碼按鈕
                self.click_position("Chip_Button")
                time.sleep(time_values[0])

                # 下注處理
                bet_types = []
                # 下大策略
                if self.bet_big:
                    bet_types.append("大")
                    self.click_position("Big_Button")
                    time.sleep(time_values[1])
                    # 點擊次數等於下注尺寸
                    for _ in range(self.bet_size - 1):  # -1是因為已經點過一次了
                        time.sleep(0.3)
                        self.click_position("Big_Button")

                # 下雙策略
                if self.bet_double:
                    bet_types.append("雙")
                    self.click_position("Dual_Button")
                    time.sleep(time_values[2])

                    for _ in range(self.bet_size - 1):
                        time.sleep(0.3)
                        self.click_position("Dual_Button")

                # 點擊下注按鈕
                self.click_position("Bet_Button")
                time.sleep(time_values[3])
                
                # 一手牌結束
                self.current_hand += 1
                
                # 儲存這手牌的資訊，但不立即記錄
                hand_info = {
                    'hand_number': self.current_hand,
                    'bet_type': " & ".join(bet_types),
                    'bet_size': self.bet_size,
                    'details': f'下注 {self.bet_size} 個籌碼尺寸 於 {" & ".join(bet_types)}'
                }
            
                # 更新 MonitorThread 中的暫存資訊
                if hasattr(self, 'monitor_thread'):
                    self.monitor_thread.previous_hand_info = hand_info
                
                # 每50手為一個round
                if self.current_hand % 50 == 0:
                    self.current_round += 1
                
                # 發送進度更新信號
                progress = {
                    'current_hand': self.current_hand,
                    'current_round': self.current_round,
                    'target_rounds': self.target_rounds,
                    'is_completed': self.current_round >= self.target_rounds
                }
                self.progress_updated.emit(progress)
                
                # 檢查是否達到目標盤數
                if self.current_round >= self.target_rounds:
                    self.running = False
                    self.waiting_for_final_record = True  # 設置等待標記

                    print("達到目標盤數，停止下注")
                    return True
                
                return False

        except Exception as e:
            print(f"下注操作時發生錯誤: {str(e)}")
            return False

    def start_betting(self):
        """開始下注流程"""
        self.running = True
        self.current_hand = 0
        self.current_round = 0
        print(f"開始下注操作 - 目標盤數: {self.target_rounds}, 下注尺寸: {self.bet_size * 1000}")

    def stop_betting(self):
        """停止下注流程"""
        if self.running:
            self.running = False
            self.waiting_for_final_record = True  # 設置等待標記
            print("停止下注操作，等待記錄最後一手結果")

    def click_position(self, element_name):
        """點擊指定位置"""
        try:
            if element_name in self.positions:
                pos = self.positions[element_name]
                pyautogui.click(pos['x'], pos['y'])
                print(f"點擊 {element_name}: ({pos['x']}, {pos['y']})")
            else:
                print(f"找不到元件位置: {element_name}")
        except Exception as e:
            print(f"點擊 {element_name} 時發生錯誤: {str(e)}")

    def get_progress(self):
        """取得目前進度"""
        return {
            'current_hand': self.current_hand,
            'current_round': self.current_round,
            'target_rounds': self.target_rounds
        }