# MQTT Configuration
MQTT_BROKER_ADDRESS = "172.30.1.86"  # MQTT 브로커 주소
MQTT_PORT = 1883  # MQTT 브로커 포트 (기본값 1883)

# Topics
TOPICS = ["img", "temp", "hum", "lumi"]

# 저장 경로 설정
IMAGE_SAVE_PATH = "C:\\Users\\Android\\Desktop\\mos\\LSP\\static\\image\\image.jpg"
IMAGE_ORI_PATH = "C:\\Users\\Android\\Desktop\\mos\\LSP\\static\\ori\\image.jpg"
JSON_PATH = "C:\\Users\\Android\\Desktop\\mos\\LSP\\static\\data.json"

# OpenPose Model Net
PROTOFILE = "pose_deploy.prototxt"
WEIGHTSFILE = "pose_iter_584000.caffemodel"

# 임계값 설정
ANGLE_THRESHOLD = 30 # 목 각도 임계값
TEMP_THRESHOLD = 20  # 온도 임계값
HUM_THRESHOLD = 60  # 습도 임계값
LUMI_THRESHOLD = 400  # 조도 임계값


