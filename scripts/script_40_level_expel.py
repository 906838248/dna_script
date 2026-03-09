from src.base_automation import BaseAutomationThread
import pyautogui
import keyboard
import pydirectinput

class Script40LevelExpel(BaseAutomationThread):
    SCRIPT_NAME = "40级魔之楔驱离"
    SCRIPT_DESCRIPTION = "刚需黎瑟"
    SCRIPT_IMG_FOLDER = "img/common"

    def run(self):
        def game_logic():
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
            return True
        
        if self.run_game_loop(game_logic, again_timeout=5):
            self.log_signal.emit("\n所有循环已完成！")
            self.finished_signal.emit()
