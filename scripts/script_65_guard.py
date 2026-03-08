from src.base_automation import BaseAutomationThread
import pyautogui
import keyboard

class Script65Guard(BaseAutomationThread):
    SCRIPT_NAME = "65级扼守"
    SCRIPT_DESCRIPTION = "刚需黎瑟"
    SCRIPT_IMG_FOLDER = "img/guard"

    def run(self):  
        for i in range(self.loop_count):
            if not self.running:
                break
            # 开始游戏
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
                if(not self.game_again(again_timeout=600)):
                    self.log_signal.emit("重新开始游戏失败，尝试重试")
                    self.game_retry()
                    if not self.game_again(again_timeout=5):
                        self.log_signal.emit("重试失败，停止循环")
                        break

            # 随机空格
            self.random_space_press()

            # 跑图
            self.log_signal.emit("开始跑图")
            self.random_delay(0.5, 1.5)
            self.load_recording("guard/guard_65")
            self.play_recording()
            self.recorder.wait_for_playback(timeout=60)

            #重置位置
            self.log_signal.emit("重置位置")
            self.random_delay(0.5, 1.5)
            self.reset_position()
            self.interruptible_sleep(1.5)
            if not self.find_image("succeed.png", confidence=0.8, timeout=2):
                self.log_signal.emit("重置位置失败，重新开始")
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
            self.log_signal.emit("等待游戏结束")
            

            

            self.log_signal.emit(f"=== 第 {self.current_loop} 轮循环完成 ===")
            self.random_delay(1.5, 3.0)
        
        self.log_signal.emit("\n所有循环已完成！")
        self.finished_signal.emit()
