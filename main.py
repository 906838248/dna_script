import pyautogui
import keyboard
import threading
import time
import random

# 全局运行状态
running = False

# 热键回调函数
def toggle_hotkey():
    global running
    running = not running
    if running:
        print("\n>>> 程序已启动 (按F6停止)")
    else:
        print("\n>>> 程序已暂停 (按F6启动)")

# 设置热键
keyboard.add_hotkey('f6', toggle_hotkey)
print("程序已加载，按F6键开始/停止")
print("按Ctrl+C退出程序")

# 模拟人类行为配置
HUMAN_CONFIG = {
    'min_delay': 0.3,      # 最小延迟（秒）
    'max_delay': 1,      # 最大延迟（秒）
    'click_offset': 10,     # 点击偏移像素范围
    'recheck_delay': 0.5,  # 重新检查延迟
}

# 生成随机延迟
def human_delay():
    delay = random.uniform(HUMAN_CONFIG['min_delay'], HUMAN_CONFIG['max_delay'])
    time.sleep(delay)

# 模拟人类点击（带随机偏移和延迟）
def human_click(position):
    if position:
        # 添加随机偏移
        x_offset = random.randint(-HUMAN_CONFIG['click_offset'], HUMAN_CONFIG['click_offset'])
        y_offset = random.randint(-HUMAN_CONFIG['click_offset'], HUMAN_CONFIG['click_offset'])
        
        # 使用鼠标移动动画
        x = position[0] + x_offset
        y = position[1] + y_offset
        
        pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3))
        pyautogui.click()
        human_delay()
        return True
    return False


# 查找图片
def find_image(image_path, confidence=0.5):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            return location
        else:
            return None
    except pyautogui.ImageNotFoundException:
        return None 


# 继续挑战
def circle():
    flag = 0
    while flag == 0:
        keep = find_image(r"img/keep.png")
        if  keep:
            human_click(keep)
            human_click(keep)
            continue
        else:
            print("未找到keep.png")
            human_delay()
            flag += 1
    while flag == 1:
        begin = find_image(r"img/begin.png")
        if begin:
            human_click(begin)
            continue
        else:
            print("未找到begin.png")
            human_delay()
            flag += 1
            

# 离开
def leave():
    last = find_image(r"img/last.png")
    if last:
        human_delay()  # 点击last后等待一下
        left = find_image(r"img/left.png")
        if left:
            human_click(left)
            return True
        else:
            print("未找到left.png")
            return False
    else:
        print("未找到last.png")
        return False

if __name__ == '__main__':
    try:
        while True:
            if running:
                leave()
                circle()
                # 循环间的随机延迟，模拟人类思考或休息
                time.sleep(random.uniform(5, 10))
            else:
                # 等待一小段时间，避免CPU占用过高
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n程序已退出")
        
            