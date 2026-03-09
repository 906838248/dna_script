from src.base_automation import BaseAutomationThread
import pyautogui
class Script60LevelExpel(BaseAutomationThread):
    SCRIPT_NAME = "60级魔之楔驱离"
    SCRIPT_DESCRIPTION = "刚需黎瑟"
    SCRIPT_IMG_FOLDER = "img/common"

    def run(self):  
        for i in range(self.loop_count):
            if not self.running:
                break
            
            self.current_loop = i + 1
            self.progress_signal.emit(self.current_loop, self.loop_count)
            self.log_signal.emit(f"\n=== 开始第 {self.current_loop} 轮循环 ===")
            
            if self.current_loop == 1:
                self.log_signal.emit("第一次进入游戏")
                if not self.game_first():
                    self.log_signal.emit("第一次进入游戏失败，尝试重新开始")
                    if not self.game_again(again_timeout=5):
                        self.log_signal.emit("重新开始游戏失败")
            else:
                self.log_signal.emit("重新开始游戏")
                if(not self.game_again(again_timeout=600)):
                    self.log_signal.emit("重新开始游戏失败，尝试重试")
                    self.game_retry()
                    if not self.game_again(again_timeout=5):
                        self.log_signal.emit("重试失败，停止循环")
                        break
            
            self.random_delay(2, 3)
            pyautogui.press('q')
            self.log_signal.emit("按下 q 键")
            self.log_signal.emit("等待游戏结束...")

        
        self.log_signal.emit("\n所有循环已完成！")
        self.finished_signal.emit()
