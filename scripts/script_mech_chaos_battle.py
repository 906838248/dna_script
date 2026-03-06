from src.base_automation import BaseAutomationThread
import pyautogui

class ScriptMechChaosBattle(BaseAutomationThread):
    def run(self):
        for i in range(self.loop_count):
            if not self.running:
                break
            
            self.current_loop = i + 1
            self.progress_signal.emit(self.current_loop, self.loop_count)
            self.log_signal.emit(f"\n=== 开始第 {self.current_loop} 轮循环 ===")
            
            if not self.click_image("star1.png", timeout=30):
                self.log_signal.emit("点击 star1 失败，停止循环")
                break
            
            self.random_delay(1.5, 2.5)
            
            self.log_signal.emit("等待游戏加载...")
            if not self.click_image("star2.png", timeout=60):
                self.log_signal.emit("等待 star2 超时，停止循环")
                break
            
            self.random_delay(0.8, 1.5)
            
            if not self.click_image("star3.png", timeout=30):
                self.log_signal.emit("点击 star3 失败，停止循环")
                break
            
            self.random_delay(0.8, 1.5)
            
            if not self.click_image("star4.png", timeout=30):
                self.log_signal.emit("点击 star4 失败，停止循环")
                break
            
            self.random_delay(0.8, 1.5)
            
            self.log_signal.emit("按下 ESC 键")
            pyautogui.press('esc')
            
            self.random_delay(0.8, 1.5)
            
            if not self.click_image("star5.png", timeout=30):
                self.log_signal.emit("点击 star5 失败，停止循环")
                break
            
            self.random_delay(0.8, 1.5)
            
            if not self.click_image("star6.png", timeout=30):
                self.log_signal.emit("点击 star6 失败，停止循环")
                break
            
            self.random_delay(0.8, 1.5)
            
            self.log_signal.emit("等待游戏结束...")
            if not self.click_image("exit.png", timeout=60):
                self.log_signal.emit("等待 exit 超时，停止循环")
                break
            
            self.log_signal.emit(f"=== 第 {self.current_loop} 轮循环完成 ===")
            self.random_delay(1.5, 3.0)
        
        self.log_signal.emit("\n所有循环已完成！")
        self.finished_signal.emit()
