import cv2
import numpy as np
import os
import math
from config import IMAGE_SAVE_PATH, PROTOFILE, WEIGHTSFILE

# OpenPose 모델을 사용하기 위한 네트워크 초기화
op_net = cv2.dnn.readNetFromCaffe(PROTOFILE, WEIGHTSFILE)

def getKeypoints(probMap, threshold=0.1):
    """ 확률 맵에서 키포인트 추출하는 함수.
    probMap: 각 키포인트 위치에 대한 확률 맵
    threshold: 키포인트를 추출하기 위한 최소 확률 임계값 """
    mapSmooth = cv2.GaussianBlur(probMap, (3, 3), 0, 0)
    mapMask = np.uint8(mapSmooth > threshold)
    keypoints = []
    contours, _ = cv2.findContours(mapMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 각 컨투어에 대해 가장 높은 확률을 가진 키포인트를 추출
    for cnt in contours:
        blobMask = np.zeros(mapMask.shape)
        blobMask = cv2.fillConvexPoly(blobMask, cnt, 1)
        maskedProbMap = mapSmooth * blobMask
        _, maxVal, _, maxLoc = cv2.minMaxLoc(maskedProbMap)
        keypoints.append(maxLoc + (probMap[maxLoc[1], maxLoc[0]],))
    return keypoints

def calculate_neck_angle(nose, neck):
    """ 코와 목 사이의 각도를 계산하는 함수.
    nose: 코의 위치
    neck: 목의 위치 """
    if nose and neck:
        horizontal_line = (1, 0)  # x축 방향의 수평선
        neck_nose_line = (neck[0] - nose[0], neck[1] - nose[1])
        angle = np.arctan2(neck_nose_line[1], neck_nose_line[0]) - np.arctan2(horizontal_line[1], horizontal_line[0])
        return np.degrees(angle)
    else:
        return None

def draw_keypoints_and_angle(frame, nose_point, neck_point, angle):
    """ 이미지에 키포인트, 선 및 각도를 그리는 함수.
    frame: 이미지 프레임
    nose_point: 코의 위치
    neck_point: 목의 위치
    angle: 계산된 각도 """
    if nose_point and neck_point:
        # 키포인트 그리기
        cv2.circle(frame, (int(nose_point[0]), int(nose_point[1])), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
        cv2.circle(frame, (int(neck_point[0]), int(neck_point[1])), 8, (0, 255, 0), thickness=-1, lineType=cv2.FILLED)

        # 코와 목 사이의 선 그리기
        cv2.line(frame, (int(nose_point[0]), int(nose_point[1])), (int(neck_point[0]), int(neck_point[1])), (255, 0, 0), 2)

        # 목 지점에서 수평선 그리기
        cv2.line(frame, (int(neck_point[0]) - 50, int(neck_point[1])), (int(neck_point[0]) + 50, int(neck_point[1])), (255, 0, 0), 2)

        # 각도 표시
        cv2.putText(frame, "Angle : {:.2f}".format(angle), (int(neck_point[0] + 30), int(neck_point[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,153), 2)

def process_image(image_ori_path, net=op_net, threshold=0.1):
    """ 이미지를 처리하고 목 자세 각도를 계산하는 함수.
    image_ori_path: 처리할 이미지의 경로
    net: OpenPose 모델 네트워크
    threshold: 키포인트 검출 임계값 """
    frame = cv2.imread(image_ori_path)
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]

    # OpenPose 네트워크에 이미지 입력
    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (368, 368), (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inpBlob)
    output = net.forward()

    # 코와 목의 키포인트 검출
    nose_probMap = output[0, 0, :, :]  # 코에 대한 인덱스 0
    neck_probMap = output[0, 1, :, :]  # 목에 대한 인덱스 1
    nose_probMap = cv2.resize(nose_probMap, (frameWidth, frameHeight))
    neck_probMap = cv2.resize(neck_probMap, (frameWidth, frameHeight))

    nose_keypoints = getKeypoints(nose_probMap, threshold)
    neck_keypoints = getKeypoints(neck_probMap, threshold)

    # 코와 목 키포인트가 모두 있는 경우에만 계산
    if nose_keypoints and neck_keypoints:
        nose_point = nose_keypoints[0][:2]
        neck_point = neck_keypoints[0][:2]

        # 각도 계산
        angle = calculate_neck_angle(nose_point, neck_point)
        
        # 90도 이상의 각도는 반대 방향으로 계산
        if angle > 90:
            angle = 180 - angle

        # 이미지에 키포인트와 각도 표시
        draw_keypoints_and_angle(frame, nose_point, neck_point, angle)

        # 이미지 저장
        cv2.imwrite(IMAGE_SAVE_PATH, frame)

        return angle
    else:
        # 키포인트가 없는 경우 이미지만 저장
        cv2.imwrite(IMAGE_SAVE_PATH, frame)
        return None
