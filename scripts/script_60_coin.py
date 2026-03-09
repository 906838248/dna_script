from src.base_automation import BaseAutomationThread
import pyautogui
class Script60Coin(BaseAutomationThread):
    SCRIPT_NAME = "60级皎皎币"
    SCRIPT_DESCRIPTION = "刚需黎瑟"
    SCRIPT_IMG_FOLDER = "img/coin/65"

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
            if self.find_image("map1.png", timeout=3):
                
                self.log_signal.emit("进入游戏,当前为初始房间类型一")

                self.log_signal.emit("开始走出房间一")
                self.load_recording("coin/65/map1")
                self.play_recording()
                self.recorder.wait_for_playback(timeout=60)
                self.interruptible_sleep(1.5)

                if self.find_image("map1_1.png", timeout=3):
                    self.log_signal.emit("确认为初始房间类型一地图类型一")
                    self.load_recording("coin/65/map1_1")
                    self.play_recording()
                    self.recorder.wait_for_playback(timeout=300)
                
                elif self.find_image("map1_2.png", timeout=3):
                    self.log_signal.emit("确认为初始房间类型一地图类型二")
                    self.load_recording("coin/65/map1_2")
                    self.play_recording()
                    self.recorder.wait_for_playback(timeout=300)
            
            elif self.find_image("map2.png", timeout=3):
                    self.log_signal.emit("确认为初始房间类型二")
                    if not self.game_retry():
                        self.log_signal.emit("重试失败，停止循环")
                        break
                    i -= 1
                    continue
            





            if not self.find_image("succeed.png", confidence=0.8, timeout=2):
                self.log_signal.emit("游戏开始失败，重新开始")
                if not self.game_retry():
                    self.log_signal.emit("重试失败，停止循环")
                    break
                self.current_loop -= 1
                continue

            # 开始刷本
            self.log_signal.emit("开始刷本")
            self.random_delay(0.5, 1.5)
            pyautogui.press('q')
            self.log_signal.emit("按下 q 键")
            
            self.log_signal.emit("等待游戏结束...")
        
        self.log_signal.emit("\n所有循环已完成！")
        self.finished_signal.emit()
