from src.base_automation import BaseAutomationThread
import pyautogui

class Script60LevelExpel(BaseAutomationThread):
    SCRIPT_NAME = "60级魔之楔驱离"
    SCRIPT_DESCRIPTION = "刚需黎瑟"
    SCRIPT_IMG_FOLDER = "img/common"

    def run(self):
        def game_logic():
            self.random_delay(2, 3)
            pyautogui.press('q')
            self.log_signal.emit("按下 q 键")
            self.log_signal.emit("等待游戏结束...")
            return True
        
        if self.run_game_loop(game_logic):
            self.log_signal.emit("\n所有循环已完成！")
            self.finished_signal.emit()
