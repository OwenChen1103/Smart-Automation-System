import csv
import os
from datetime import datetime

class BettingLogger:
    def __init__(self):
        self.log_dir = "betting_logs"
        self.ensure_log_directory()
        self.current_log_file = self.create_new_log_file()
        
    def ensure_log_directory(self):
        """確保日誌目錄存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
    def create_new_log_file(self):
        """建立新的日誌檔案"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.log_dir, f"betting_log_{timestamp}.csv")
        
        # 建立CSV檔案並寫入標題
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['時間', '手數', '下注類型', '下注尺寸', '狀態', '詳細資訊', '遊戲結果'])

            
        return filename
    
    def log_result(self, result):
        """記錄每次下注結果"""
        try:
            with open(self.current_log_file, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([
                    result.get('timestamp', ''),
                    result.get('hand_number', ''),
                    result.get('bet_type', ''),
                    result.get('bet_size', ''),
                    result.get('status', ''),
                    result.get('details', ''),
                    result.get('game_result', '')
                ])
        except Exception as e:
            print(f"記錄結果時發生錯誤: {str(e)}")