from src.base_automation import BaseAutomationThread
import pyautogui

class ScriptRadBall(BaseAutomationThread):
    SCRIPT_NAME = "深红凝珠"
    SCRIPT_DESCRIPTION = "刚需赛琪,带齐奶妈避免血量过低"
    SCRIPT_IMG_FOLDER = "img/escort"

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
                        break
            else:
                self.log_signal.emit("重新开始游戏")
                if(not self.game_again(again_timeout=5)):
                    self.log_signal.emit("重新开始游戏失败，尝试重试")
                    self.game_retry()
                    if not self.game_again(again_timeout=5):
                        self.log_signal.emit("重试失败，停止循环")
                        break

                
            
            
            self.random_delay(0.5, 1.5)
            self.log_signal.emit("进入游戏,当前为房间一")

            self.log_signal.emit("开始走出房间一")
            self.load_recording("rad_ball/rad_ball_1")
            self.play_recording()
            self.recorder.wait_for_playback(timeout=60)
            pyautogui.press('q')
            self.log_signal.emit("按下 q 键")
            self.interruptible_sleep(2)
            
            


            if self.find_image("map1.png", timeout=3):
                self.log_signal.emit("确认为地图类型一")
                self.load_recording("rad_ball/map1_1")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/map1_2")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/map1_3")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)

            elif self.find_image("map2.png", timeout=3):
                self.log_signal.emit("确认为地图类型二")
                self.load_recording("rad_ball/map2_1")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/map2_2")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/map2_3")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
            elif self.find_image("map3.png", timeout=3):
                self.log_signal.emit("确认为地图类型三")
                self.load_recording("rad_ball/map3_1")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/map3_2")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/map3_3")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)

            elif self.find_image("map4.png", timeout=3):
                self.log_signal.emit("确认为地图类型四")
                self.load_recording("rad_ball/map4_1")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/map4_2")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)
                self.load_recording("rad_ball/map4_3")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=300)

            else:
                self.log_signal.emit("未知地图类型")

            

            
        
        self.log_signal.emit("\n所有循环已完成！")
        self.finished_signal.emit()
