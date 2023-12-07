import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import EnvironmentMonitor
import camera
import LEDControl
import time
import cv2

# MQTT 설정
mqtt_client = mqtt.Client()
mqtt_broker_ip = "172.30.1.86"  # MQTT 브로커의 IP 주소

# GPIO 설정
study_mode_button = 21  # GPIO21 핀에 연결된 버튼
GPIO.setmode(GPIO.BCM)
GPIO.setup(study_mode_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 공부 모드 상태
study_mode = False

# 환경 임계값 설정
TEMP_THRESHOLD = 20  # 온도 임계값
HUM_THRESHOLD = 60  # 습도 임계값
LUMI_THRESHOLD = 400  # 조도 임계값

# 버튼 콜백 함수
def button_callback(channel):
    global study_mode
    study_mode = not study_mode
    if study_mode:
        LEDControl.control_study_mode_led(True)  # 공부 모드 시작 시 빨간 LED 켜기
        print("공부 모드 시작!")
        mqtt_connect()  # MQTT 통신 시작
    else:
        LEDControl.control_study_mode_led(False)  # 공부 모드 종료 시 빨간 LED 끄기
        LEDControl.control_threshold_led(False)   # 초록 LED도 끄기
        print("공부 모드 종료.")
        mqtt_disconnect()  # MQTT 통신 종료

# 버튼 이벤트 감지 설정
GPIO.add_event_detect(study_mode_button, GPIO.RISING, callback=button_callback, bouncetime=200)

# MQTT 연결 함수
def mqtt_connect():
    mqtt_client.connect(mqtt_broker_ip, 1883, 60)
    mqtt_client.loop_start()

# MQTT 해제 함수
def mqtt_disconnect():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

# 센서 데이터 발행 및 LED 제어 함수
def publish_sensor_data():
    if study_mode:  # 공부 모드 활성화 시 실행
        temperature = EnvironmentMonitor.get_temperature()
        humidity = EnvironmentMonitor.get_humidity()
        luminance = EnvironmentMonitor.get_luminance()

        # LED 상태 결정 및 제어
        if (temperature > TEMP_THRESHOLD + 3 or temperature < TEMP_THRESHOLD - 3 or
            humidity > HUM_THRESHOLD + 30 or humidity < HUM_THRESHOLD - 30 or
            luminance > LUMI_THRESHOLD + 250 or luminance < LUMI_THRESHOLD - 250):
            LEDControl.control_threshold_led(True)  # 임계값 초과 시 초록 LED 켜기
        else:
            LEDControl.control_threshold_led(False)  # 임계값 내 시 초록 LED 끄기

        # MQTT를 통한 센서 데이터 발행
        mqtt_client.publish("temp", str(temperature))
        mqtt_client.publish("hum", str(humidity))
        mqtt_client.publish("lumi", str(luminance))

        # 카메라로 사진 촬영 및 MQTT를 통해 전송
        image = camera.take_picture()
        _, encoded_image = cv2.imencode('.jpg', image)
        image_bytes = bytearray(encoded_image)
        mqtt_client.publish("img", image_bytes)

# 카메라 초기화
camera.init()

# 프로그램 시작 메시지
print("Let's study Properly")
print("")

# 메인 루프
try:
    while True:
        if study_mode:
            publish_sensor_data()  # 공부 모드 시 센서 데이터 발행
            time.sleep(4)  # 데이터 발행 간격
except KeyboardInterrupt:
    GPIO.cleanup()  # GPIO 정리
    camera.final()   # 카메라 종료
    mqtt_disconnect()  # MQTT 연결 해제
