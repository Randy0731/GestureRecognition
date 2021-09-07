import RPi.GPIO as GPIO
import time
import speech_recognition as sr
import re
import cv2
import numpy as np
from gtts import gTTS
import os
# mardo GPIO PIN
PWM_FREQ = 50
STEP=15
chan_list=[11,13,15,19,21]
GPIO.setmode(GPIO.BOARD)
GPIO.setup(chan_list, GPIO.OUT)
finger1 = GPIO.PWM(11, PWM_FREQ)
finger2= GPIO.PWM(13, PWM_FREQ)
finger3= GPIO.PWM(15, PWM_FREQ)
finger4= GPIO.PWM(19, PWM_FREQ)
finger5= GPIO.PWM(21, PWM_FREQ)
finger1.start(0)
finger2.start(0)
finger3.start(0)
finger4.start(0)
finger5.start(0)

# compute angle
def angle_to_duty_cycle(angle=0):
    duty_cycle = (0.05 * PWM_FREQ) + (0.19 * PWM_FREQ * angle / 180)
    return duty_cycle

# voice recognize
def voice_recognize():
    get_strings=""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please wait. Calibrating microphone...")
        # listen for 1 seconds and create the ambient noise energy level
        r.adjust_for_ambient_noise(source, duration=1)
        print("Say something!")
        audio = r.listen(source)
    # recognize speech using Google Speech Recognition
    try:
        print("Google Speech Recognition thinks you said:")
        get_strings=r.recognize_google(audio, language='zh-TW')
        print(get_strings)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("No response from Google Speech Recognition service: {0}".format(e))
    # Whether valid
    if re.findall('[a-pr-z]+', get_strings.lower()):  # 檢查是否包含字母
        print("輸入錯誤，包含非法字符!")
    else:
        get_strings = get_strings.replace("加", "+")
        get_strings = get_strings.replace("減", "-")
        get_strings = get_strings.replace("乘", "*")
        get_strings = get_strings.replace("除", "/")
        replace_stars = multiply_divide(get_strings)  # 乘除運算
        get_strings = get_strings.replace(get_strings, replace_stars)
        replace_stars = add_minus(get_strings)  # 加減運算
        get_strings = get_strings.replace(get_strings, replace_stars)
        print(get_strings)

        if(int(float(get_strings))==1):
            one()
        elif(int(float(get_strings))==2):
            two()
        elif (int(float(get_strings)) == 3):
            three()
        elif (int(float(get_strings)) == 4):
            four()
        elif (int(float(get_strings)) == 5):
            five()
        tts = gTTS(text='輸出手勢為'+str(int(float(get_strings)))+',請確認', lang='zh-TW')
        tts.save('voice.mp3')
        os.system('omxplayer -o local -p voice.mp3 > /dev/null 2>&1')
        time.sleep(2)
# 格式化字符串函數(消除一些錯誤的格式)
def format_string(string):
    # 一系列的替換語句
    string = string.replace("--", "-")
    string = string.replace("-+", "-")
    string = string.replace("+-", "-")
    string = string.replace("++", "+")
    string = string.replace("*+", "*")
    string = string.replace("/+", "/")
    string = string.replace(" ", "-")
    return string

# 加減法函數
def add_minus(string):
    add_regular = r'[\-]?\d+\.?\d*\+[\-]?\d+\.?\d*'       # 定義一個匹配的規則
    sub_regular = r'[\-]?\d+\.?\d*\-[\-]?\d+\.?\d*'       # 同上
# 註解：[\-]? 如果有負號，匹配負號； \d+ 匹配最少一個數字； \.? 是否有小數點，有就匹配；\d* 是否有數字有就匹配
# \+ 匹配一個加號；  [\-]?\d+\.?\d*  這幾個同上
    # 加法
    while re.findall(add_regular, string):    # 按照regular規則獲取一個表達式,用while循環，把所有加法都算完
        add_list = re.findall(add_regular, string)
        for add_stars in add_list:
            x, y = add_stars.split('+')      # 獲取兩個做加法的數(以+號作為分割對象)，分別賦給x和y
            add_result = '+' + str(float(x) + float(y))
            string = string.replace(add_stars, add_result)   # 替換
        string = format_string(string)
    # 減法
    while re.findall(sub_regular, string):    # 用while循環，把所有減法都算完
        sub_list = re.findall(sub_regular, string)
        for sub_stars in sub_list:
            x, y = sub_stars.split('-')  # 獲取兩個做減法的數(以-號作為分割對象)，分別賦給x和y
            sub_result = '+' + str(float(x) - float(y))
            string = string.replace(sub_stars, sub_result)   # 替換
        string = format_string(string)
    return string

# 乘、除法函數
def multiply_divide(string):
    regular = r'[\-]?\d+\.?\d*[*/][\-]?\d+\.?\d*'  # 定義一個匹配的規則regular
    while re.findall(regular, string):
        expression = re.search(regular, string).group()    # 按照regular規則獲取一個表達式
        # 如果是乘法
        if expression.count('*') == 1:
            x, y = expression.split('*')
            mul_result = str(float(x) * float(y))
            # print("xXX"+mul_result)
            string = string.replace(expression, mul_result)  # 計算結果替換原表達式
            string = format_string(string)  # 格式化
        # 如果是除法
        if expression.count('/') == 1:
            x, y = expression.split('/')
            div_result = str(float(x) / float(y))
            # print("xXX"+div_result)
            string = string.replace(expression, div_result)
            string = format_string(string)  # 格式化
    return string

# finger rotate
def one():
    finger1.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger2.ChangeDutyCycle(angle_to_duty_cycle(0))
    finger3.ChangeDutyCycle(angle_to_duty_cycle(-10))
    finger4.ChangeDutyCycle(angle_to_duty_cycle(0))
    finger5.ChangeDutyCycle(angle_to_duty_cycle(-20))
def two():
    finger1.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger2.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger3.ChangeDutyCycle(angle_to_duty_cycle(-10))
    finger4.ChangeDutyCycle(angle_to_duty_cycle(0))
    finger5.ChangeDutyCycle(angle_to_duty_cycle(-20))
def three():
    finger1.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger2.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger3.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger4.ChangeDutyCycle(angle_to_duty_cycle(0))
    finger5.ChangeDutyCycle(angle_to_duty_cycle(-20))
def four():
    finger1.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger2.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger3.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger4.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger5.ChangeDutyCycle(angle_to_duty_cycle(-20))
def five():
    finger1.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger2.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger3.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger4.ChangeDutyCycle(angle_to_duty_cycle(90))
    finger5.ChangeDutyCycle(angle_to_duty_cycle(90))

# guesture recognize
def cappp():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print('press "s" to start')
    while(True):
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
    #cv2.destroyAllWindows()
    start_time = time.time()
    num_list = [ 0, 0, 0, 0, 0, 0]
    #            1,  , 2, 3, 4, 5
    while time.time() - start_time < 5:
        ret, frame = cap.read()
        fgbg = cv2.createBackgroundSubtractorMOG2()
        fgmask = fgbg.apply(frame)
        kernel = np.ones((5, 5), np.uint8)
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        res = cv2.bitwise_and(frame, frame, mask=fgmask)
        ycrcb = cv2.cvtColor(res, cv2.COLOR_BGR2YCrCb)
        (_, cr, _) = cv2.split(ycrcb)
        cr1 = cv2.GaussianBlur(cr, (5, 5), 0)
        _, skin = cv2.threshold(cr1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cv2.imshow('frame', skin)
        contours, hierarchy = cv2.findContours(skin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = max(contours, key=lambda x: cv2.contourArea(x))
        hull = cv2.convexHull(contours, returnPoints=False)
        defects = cv2.convexityDefects(contours, hull)
        cnt = 0
        if defects is not None:
            cnt = 0
        for i in range(defects.shape[0]):  # calculate the angle
            s, e, f, d = defects[i][0]
            start = tuple(contours[s][0])
            end = tuple(contours[e][0])
            far = tuple(contours[f][0])
            a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))  #      cosine theorem
            if angle <= np.pi / 2:  # angle less than 90 degree, treat as fingers
                cnt += 1
        if cnt > 0:
            cnt = cnt+1
        if cnt>5:
            cnt=5
        num_list[cnt] += 1
    num_list[1] = num_list[0]
    max_ = 1
    for i in range(4):
        if num_list[i + 2] > num_list[max_]:
            max_ = i + 2
    cv2.destroyAllWindows()
    #max_ 為 要比的數字
    if (max_ == 1):
        one()
    elif (max_ == 2):
        two()
    elif (max_ == 3):
        three()
    elif (max_ == 4):
        four()
    elif (max_ == 5):
        five()
    print("MAXXXXXXXXXXXXXXXXX: "+str(max_))
    tts = gTTS(text='輸出手勢為' + str(max_)+',請確認', lang='zh-TW')
    tts.save('voice.mp3')
    os.system('omxplayer -o local -p voice.mp3 > /dev/null 2>&1')
    time.sleep(2)
# main
while True:
    print("1. Camera Recognization:")
    print("2. Voice  Recognization:")
    types=input(">>>")

    if types=="1":
        cappp()
    elif types=="2":
        voice_recognize()
    elif types=="q":
        print("Exit the Program!")
        break

finger1.stop()
finger2.stop()
finger3.stop()
finger4.stop()
finger5.stop()
GPIO.cleanup()