import subprocess
from PIL import Image
import re
import os
import time

# ========= 用户自行配置全部参数 =========
# rish二进制完整路径
RISH_PATH = ""
# 截图输出路径
screen_path = ""
# 裁剪图输出路径
crop_path = ""

# 画面裁剪框 (x1,y1,x2,y2)
CROP_BOX = ()

# 手势坐标，屏幕指针位置
GT_P1 = ()
GT_P2 = ()
GT_P3 = ()

LT_P1 = ()
LT_P2 = ()
LT_P3 = ()

SWIPE_DUR = 40
GESTURE_INTERVAL = 0.3
LOOP_GESTURE_CNT = 20
# =======================================

while True:
    time.sleep(0.12)
    print("\n---新一轮识别---")
    try:
        subprocess.run([RISH_PATH, "-c", f"screencap -p {screen_path}"], timeout=3)
        os.sync()

        img = Image.open(screen_path)
        crop_img = img.crop(CROP_BOX)
        crop_img.save(crop_path)

        res = subprocess.run(
            ["tesseract", crop_path, "-", "--psm", "7"],
            capture_output=True,
            text=True,
            timeout=3
        )
        text = res.stdout.strip()
        print(f"识别文本：{repr(text)}")
        nums = re.findall(r"\d+", text)

        for f in (screen_path, crop_path):
            try:
                os.remove(f)
            except Exception:
                pass

        if len(nums) >= 2:
            a = int(nums[0])
            b = int(nums[1])
            print(f"待比较 A={a}, B={b}")
            toggle = True
            for i in range(LOOP_GESTURE_CNT):
                if toggle:
                    print(f"[{i+1}]绘制大于号 >")
                    gesture = (f"input swipe {GT_P1[0]} {GT_P1[1]} {GT_P2[0]} {GT_P2[1]} {SWIPE_DUR};"
                               f"input swipe {GT_P2[0]} {GT_P2[1]} {GT_P3[0]} {GT_P3[1]} {SWIPE_DUR}")
                else:
                    print(f"[{i+1}]绘制小于号 <")
                    gesture = (f"input swipe {LT_P1[0]} {LT_P1[1]} {LT_P2[0]} {LT_P2[1]} {SWIPE_DUR};"
                               f"input swipe {LT_P2[0]} {LT_P2[1]} {LT_P3[0]} {LT_P3[1]} {SWIPE_DUR}")
                subprocess.run([RISH_PATH, "-c", gesture], timeout=2)
                toggle = not toggle
                time.sleep(GESTURE_INTERVAL)
        else:
            print("识别不到两个数字，跳过")

    except subprocess.TimeoutExpired:
        print("⚠️ rish超时，Shizuku异常，本轮跳过")
    except Exception as e:
        print(f"⚠️异常：{e}")
