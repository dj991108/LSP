from flask import Flask, jsonify, render_template
import datetime
import os
import json
from config import JSON_PATH

app = Flask(__name__)

# JSON 파일에서 데이터 로드
def load_data_from_file():
    with open(JSON_PATH, "r", encoding="utf-8") as file:  # UTF-8 인코딩 명시
        return json.load(file)

@app.route('/')
def index():
    return render_template('LSP.html')

@app.route('/posture')
def get_posture():
    # 'static/image' 폴더에서 최신 이미지 파일 찾기
    image_folder = 'static/image'
    image_files = os.listdir(image_folder)
    latest_image = max(image_files, key=lambda x: os.path.getctime(os.path.join(image_folder, x)))

    # JSON 파일에서 posture_status 로드
    data = load_data_from_file()
    posture_status = data.get("angle_advice", "정보 없음")  # 기본값 설정

    return jsonify({
        "image": latest_image,
        "status": posture_status
    })

@app.route('/environment')
def get_environment():
    data = load_data_from_file()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
