import pyscreenshot as ps
from PIL import Image
import cv2
import numpy as np
from matplotlib import pyplot as plt
from pprint import pprint
import pyautogui
import threading

need_detect = False
ax = 375
ay = 110
game_width = 290
game_height = 470


def screen_shot():
    im1 = pyautogui.screenshot(region=(ax, ay, game_width, game_height))
    im1.save('capture.png')


def find_if_close(cnt1, cnt2):
    row1, row2 = cnt1.shape[0], cnt2.shape[0]
    for i in range(row1):
        for j in range(row2):
            dist = np.linalg.norm(cnt1[i] - cnt2[j])
            if abs(dist) < 50:
                return True
            elif i == row1 - 1 and j == row2 - 1:
                return False


def process_image():
    global need_detect

    img = cv2.imread('capture.png', 0)
    ret, thresh = cv2.threshold(img, 127, 255, 0)
    contours, hier = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 2)

    LENGTH = len(contours)

    if LENGTH > 50:
        need_detect = False
        return

    need_detect = True

    status = np.zeros((LENGTH, 1))

    for i, cnt1 in enumerate(contours):
        x = i
        if i != LENGTH - 1:
            for j, cnt2 in enumerate(contours[i + 1:]):
                x = x + 1
                dist = find_if_close(cnt1, cnt2)
                if dist == True:
                    val = min(status[i], status[x])
                    status[x] = status[i] = val
                else:
                    if status[x] == status[i]:
                        status[x] = i + 1

    unified = []
    maximum = int(status.max()) + 1
    for i in range(maximum):
        pos = np.where(status == i)[0]
        if pos.size != 0:
            cont = np.vstack(contours[i] for i in pos)
            hull = cv2.convexHull(cont)
            unified.append(hull)

    cv2.drawContours(img, unified, -1, (0, 255, 0), 2)
    cv2.drawContours(thresh, unified, -1, 255, -1)

    cv2.imwrite('processed.png', thresh)


def detect_captcha():
    if need_detect == False:
        return

    im = cv2.imread('processed.png', 0)
    im = cv2.bitwise_not(im)
    detector = cv2.SimpleBlobDetector_create()
    keypoints = detector.detect(im)

    is_captcha = (len(keypoints) == 2)

    pprint(len(keypoints))

    if is_captcha:
        pprint('Found captcha!')
        if keypoints[0].pt[1] > keypoints[1].pt[1]:
            solve_captcha(keypoints[1], keypoints[0])
        else:
            solve_captcha(keypoints[0], keypoints[1])
    else:
        pprint('Captcha not detected!')


def solve_captcha(keypoint1, keypoint2):
    pprint('Solving captcha...')
    pyautogui.moveTo(ax + keypoint1.pt[0], ay + keypoint1.pt[1])
    pyautogui.dragTo(ax + keypoint2.pt[0], ay + keypoint2.pt[1], 1, button = 'left')


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def bot():
    pprint('Bot is running...')
    screen_shot()
    process_image()
    detect_captcha()

bot()
set_interval(bot, 60)



