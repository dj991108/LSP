import time
import RPi.GPIO as GPIO
import Adafruit_MCP3008
from adafruit_htu21d import HTU21D
import busio

""" 조도 측정 """
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
mcp = Adafruit_MCP3008.MCP3008(clk=11, cs=8, miso=9, mosi=10)

def get_luminance(mcp=mcp):
    try:
        return mcp.read_adc(0)
    except Exception as e:
        print(f"조도 센서 오류: {e}")
        return None

""" 온도 / 습도 측정 """

sda = 2 # GPIO2 핀. sda 이름이 붙여진 핀
scl = 3 # GPIO3 핀. scl 이름이 붙여진 핀
i2c = busio.I2C(scl, sda) # I2C 버스 통신을 실행하는 객체 생성
sensor = HTU21D(i2c) # I2C 버스에서 HTU21D 장치를 제어하는 객체 리턴

def get_temperature(sensor=sensor):
    try:
        return float(sensor.temperature)
    except Exception as e:
        print(f"온도 센서 오류: {e}")
        return None

def get_humidity(sensor=sensor):
    try:
        return float(sensor.relative_humidity)
    except Exception as e:
        print(f"습도 센서 오류: {e}")
        return None