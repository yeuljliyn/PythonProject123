import cv2
import numpy as np
from Common.utils import put_string

def zoom_bar(value):
    global zoom_factor
    # 트랙바 값(50-100)을 줌 배율(1.0-2.0)로 변환
    zoom_factor = 1.0 + (value - 50) / 50.0
    print(f"줌 설정: {zoom_factor:.1f}x")

def focus_bar(value):
    global blur_factor
    # 트랙바 값(0-20)을 블러 강도로 사용
    blur_factor = value
    print(f"초점 설정: {blur_factor}")

# 전역 변수 초기화
zoom_factor = 1.0
blur_factor = 0

capture = cv2.VideoCapture(0)								# 0번 카메라 연결
if not capture.isOpened():
    print("카메라를 열 수 없습니다. 다음을 확인해주세요:")
    print("1. 카메라가 연결되어 있는지 확인")
    print("2. 시스템 환경설정 > 보안 및 개인 정보 보호 > 개인 정보 보호 > 카메라에서 권한이 허용되어 있는지 확인")
    raise Exception("카메라 연결 실패")

# 카메라 속성 설정
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 400)      # 카메라 프레임 너비
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)     # 카메라 프레임 높이

title = "Change Camera Properties"              # 윈도우 이름 지정
cv2.namedWindow(title)                          # 윈도우 생성 - 반드시 생성 해야함

# 트랙바 생성
cv2.createTrackbar("zoom", title, 50, 100, zoom_bar)    # 줌 (시작값 50, 최대값 100)
cv2.createTrackbar("focus", title, 0, 20, focus_bar)    # 초점 (시작값 0, 최대값 20)

while True:
    ret, frame = capture.read()                 # 카메라 영상 받기
    if not ret: break
    if cv2.waitKey(30) >= 0: break

    # 좌우 반전 (거울 효과)
    frame = cv2.flip(frame, 1)  # 1은 좌우 반전, 0은 상하 반전, -1은 상하좌우 반전

    # 이미지 처리
    h, w = frame.shape[:2]
    
    # 줌 효과 적용
    if zoom_factor > 1.0:
        # 중앙 좌표 계산
        center_x, center_y = w//2, h//2
        # 새로운 크기 계산
        new_w = int(w/zoom_factor)
        new_h = int(h/zoom_factor)
        # 중앙 부분 추출
        x1 = center_x - new_w//2
        y1 = center_y - new_h//2
        x2 = center_x + new_w//2
        y2 = center_y + new_h//2
        # 이미지 자르기
        frame = frame[y1:y2, x1:x2]
        # 원래 크기로 리사이즈
        frame = cv2.resize(frame, (w, h))
    
    # 초점 효과 적용 (블러)
    if blur_factor > 0:
        # 블러 커널 크기는 홀수여야 합니다
        ksize = blur_factor * 2 + 1
        # 커널 크기가 1x1인 경우는 블러 효과가 없으므로 1보다 큰 경우에만 적용
        if ksize > 1:
             frame = cv2.GaussianBlur(frame, (ksize, ksize), 0)
    
    # 화면에 현재값 표시 (cv2.putText 사용)
    cv2.putText(frame, f"zoom: {zoom_factor:.1f}x", (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"focus: {blur_factor}", (10, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.imshow(title, frame)

capture.release()
cv2.destroyAllWindows()