import paho.mqtt.client as mqtt
import PostureAnalysis  # 이미지 분석 모듈 임포트
import json
from config import MQTT_BROKER_ADDRESS, MQTT_PORT, TOPICS, IMAGE_ORI_PATH, JSON_PATH, TEMP_THRESHOLD, HUM_THRESHOLD, LUMI_THRESHOLD, ANGLE_THRESHOLD

# 데이터 저장을 위한 딕셔너리
data_storage = {
    "temp": None,  # 현재 온도
    "temp_advice": "적당한 온도입니다.",   # 온도에 대한 조언
    "hum": None,  # 현재 습도
    "hum_advice": "적당한 습도입니다.",    # 습도에 대한 조언
    "lumi": None,  # 현재 조도
    "lumi_advice": "적당한 밝기입니다.",    # 조도에 대한 조언
    "angle": None,  # 현재 목 각도
    "angle_advice": "정상 상태",   # 거북목 상태에 대한 조언
}

# JSON 파일로 데이터 저장하는 함수
def save_data_to_file():
    with open(JSON_PATH, "w") as file:
        json.dump(data_storage, file)

# 센서 데이터를 처리하는 함수들
def handle_temp(value):
    # 온도 임계값 처리
    if value > TEMP_THRESHOLD + 3:
        data_storage["temp_advice"] = "에어컨 작동 추천!"
    elif value < TEMP_THRESHOLD - 3:
        data_storage["temp_advice"] = "히터 작동 추천!"
    else:
        data_storage["temp_advice"] = "적당한 온도입니다."
    
def handle_hum(value):
    # 습도 임계값 처리
    if value > HUM_THRESHOLD + 30:
        data_storage["hum_advice"] = "제습기 작동 추천!"
    elif value < HUM_THRESHOLD - 30:
        data_storage["hum_advice"] = "가습기 작동 추천!"
    else:
        data_storage["hum_advice"] = "적당한 습도입니다."

def handle_lumi(value):
    # 조도 임계값 처리
    if value > LUMI_THRESHOLD + 250:
        data_storage["lumi_advice"] = "너무 밝습니다!"
    elif value < LUMI_THRESHOLD - 250:
        data_storage["lumi_advice"] = "너무 어둡습니다!"
    else:
        data_storage["lumi_advice"] = "적당한 조도입니다."

# MQTT 콜백 함수들
def on_connect(client, userdata, flags, rc):
    # MQTT 브로커에 연결됐을 때의 콜백
    if rc == 0:
        print("Broker 연결 성공\n")
        # 구독 설정
        for topic in TOPICS:
            client.subscribe(topic, qos=0)
    else:
        print("Connection failed")

def on_message(client, userdata, msg):
    # MQTT 메시지 수신 시 콜백
    global data_storage  # 전역 변수 사용

    if msg.topic == "img":
        # 이미지 데이터 처리
        with open(IMAGE_ORI_PATH, 'wb') as file:
            file.write(msg.payload)
        angle = PostureAnalysis.process_image(IMAGE_ORI_PATH)
        data_storage["angle"] = angle

        if angle is None:
            # 각도 계산 불가능한 경우 처리
            print("이미지에서 사람이 감지되지 않음")
            data_storage["angle_advice"] = "공석 상태"
        else:
            # 각도 계산 가능한 경우 처리
            print("Angle:", angle)
            if angle < ANGLE_THRESHOLD:
                data_storage["angle_advice"] = "거북목 상태입니다!"
            else:
                data_storage["angle_advice"] = "정상 상태"
    else:
        try:
            # 환경 데이터 처리
            if msg.topic in data_storage:
                value = float(msg.payload.decode('utf-8'))
                data_storage[msg.topic] = value
                print(f"{msg.topic} 값 : {value}")

                # 임계값에 따른 권장사항 생성
                if msg.topic == "temp":
                    handle_temp(value)
                elif msg.topic == "hum":
                    handle_hum(value)
                elif msg.topic == "lumi":
                    handle_lumi(value)
        except ValueError:
            # 데이터 포맷 오류 처리
            print(f"Invalid data format for topic {msg.topic}: {msg.payload}")
    
    # 데이터 파일로 저장
    save_data_to_file()

# MQTT 클라이언트 설정
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT)

# MQTT 루프 시작
client.loop_forever()
