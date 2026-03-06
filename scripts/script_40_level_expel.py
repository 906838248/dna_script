from src.base_automation import BaseAutomationThread
import pyautogui
import keyboard
import time
import random
import pydirectinput

class Script40LevelExpel(BaseAutomationThread):
    def run(self):
        for i in range(self.loop_count):
            if not self.running:
                break
            
            self.current_loop = i + 1
            self.progress_signal.emit(self.current_loop, self.loop_count)
            self.log_signal.emit(f"\n=== 开始第 {self.current_loop} 轮循环 ===")
            if self.current_loop == 1:
                self.log_signal.emit("第一次进入游戏")
                if not self.game_first(first_timeout, begin_timeout, in_game_timeout):
                    self.log_signal.emit("第一次进入游戏失败，尝试重新开始")
                    if not self.game_again(again_timeout=5):
                        self.log_signal.emit("重新开始游戏失败")
                        break
            else:
                self.log_signal.emit("重新开始游戏")
            if not self.game_again(again_timeout=5):
                self.log_signal.emit("重新开始游戏失败，尝试重试")
                self.game_retry()
                if not self.game_again(again_timeout=5):
                    self.log_signal.emit("重试失败，停止循环")
                    break



            self.random_delay(1, 1.5)
            pyautogui.press('z')
            self.log_signal.emit("按下 z 键")
            self.interruptible_sleep(2)

            pydirectinput.moveRel(-270, 0)
            self.log_signal.emit("鼠标向左移动")

            keyboard.press('w')
            self.log_signal.emit("按住 w 键")
            self.interruptible_sleep(8)
            keyboard.release('w')
            self.log_signal.emit("释放 w 键")

            pyautogui.press('q')
            self.log_signal.emit("按下 q 键")    
            self.random_delay(0.8, 1.5)

            self.random_space_press()

            self.log_signal.emit("等待游戏结束...")
            
            self.log_signal.emit(f"=== 第 {self.current_loop} 轮循环完成 ===")
            self.random_delay(1.5, 3.0)
        
        self.log_signal.emit("\n所有循环已完成！")
        self.finished_signal.emit()
