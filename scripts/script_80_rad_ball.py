from src.base_automation import BaseAutomationThread
import pyautogui

class Script80RadBall(BaseAutomationThread):
    SCRIPT_NAME = "深红凝珠"
    SCRIPT_DESCRIPTION = "刚需赛琪,带齐奶妈避免血量过低"
    SCRIPT_IMG_FOLDER = "img/rad_ball/80"

    def run(self):
        def game_logic():
            self.random_delay(0.5, 1.5)
            self.log_signal.emit("进入游戏,当前为房间一")

            self.log_signal.emit("开始走出房间一")
            self.load_recording("rad_ball/80/rad_ball_80")
            self.play_recording()
            self.recorder.wait_for_playback(timeout=60)
            pyautogui.press('q')
            self.log_signal.emit("按下 q 键")
            self.interruptible_sleep(2)
            
            if self.find_image("map1.png", timeout=3):
                self.log_signal.emit("确认为地图类型一")
                self.load_recording("rad_ball/80/map1_1")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/80/map1_2")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/80/map1_3")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)

            elif self.find_image("map2.png", timeout=3):
                self.log_signal.emit("确认为地图类型二")
                self.load_recording("rad_ball/80/map2_1")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/80/map2_2")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/80/map2_3")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
            elif self.find_image("map3.png", timeout=3):
                self.log_signal.emit("确认为地图类型三")
                self.load_recording("rad_ball/80/map3_1")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/80/map3_2")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/80/map3_3")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)

            elif self.find_image("map4.png", timeout=3):
                self.log_signal.emit("确认为地图类型四")
                self.load_recording("rad_ball/80/map4_1")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/80/map4_2")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/80/map4_3")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)

            else:
                self.log_signal.emit("未知地图类型")
            
            return True
        
        if self.run_game_loop(game_logic, again_timeout=5):
            self.log_signal.emit("\n所有循环已完成！")
            self.finished_signal.emit()
