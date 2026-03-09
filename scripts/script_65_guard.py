from src.base_automation import BaseAutomationThread
import pyautogui
import keyboard

class Script65Guard(BaseAutomationThread):
    SCRIPT_NAME = "65级扼守"
    SCRIPT_DESCRIPTION = "刚需黎瑟"
    SCRIPT_IMG_FOLDER = "img/guard"

    def run(self):
        def game_logic():
            self.random_space_press()

            self.log_signal.emit("开始跑图")
            self.random_delay(0.5, 1.5)
            self.load_recording("guard/guard_65")
            self.play_recording()
            self.recorder.wait_for_playback(timeout=60)

            self.log_signal.emit("重置位置")
            self.random_delay(0.5, 1.5)
            self.reset_position()
            self.interruptible_sleep(1.5)
            
            if not self.find_image("succeed.png", confidence=0.8, timeout=2):
                self.log_signal.emit("重置位置失败，重新开始")
                return False

            self.log_signal.emit("开始刷本")
            self.random_delay(0.5, 1.5)
            pyautogui.press('q')
            self.log_signal.emit("按下 q 键")
            self.log_signal.emit("等待游戏结束")
            
            return True
        
        if self.run_game_loop(game_logic):
            self.log_signal.emit("\n所有循环已完成！")
            self.finished_signal.emit()
