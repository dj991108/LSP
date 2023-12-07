import time
import RPi.GPIO as GPIO

# LED 핀 번호 설정
LED1 = 6  # GPIO6, 빨간 LED
LED2 = 5  # GPIO5, 초록 LED

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)

# 빨간 LED 제어 함수 (공부 모드 LED)
def control_study_mode_led(state):
    GPIO.output(LED1, state)

# 초록 LED 제어 함수 (환경 임계값 LED)
def control_threshold_led(state):
    GPIO.output(LED2, state)
