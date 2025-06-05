import cv2
import time
from datetime import datetime
import numpy as np
import os

def zoom_bar(value):
    global zoom_factor
    zoom_factor = 1.0 + (value - 50) / 50.0
    print(f"줌 설정: {zoom_factor:.1f}x")

def focus_bar(value):
    global blur_factor
    blur_factor = value
    print(f"초점 설정: {blur_factor}")

def main():
    # 저장 디렉토리 설정 (상대 경로 사용)
    save_dir = "images_chap4"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"저장 디렉토리 생성됨: {save_dir}")
    
    # 전역 변수 초기화
    global zoom_factor, blur_factor
    zoom_factor = 1.0
    blur_factor = 0
    
    # 카메라 열기
    cap = cv2.VideoCapture(0)
    
    # 카메라 설정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # 트랙바 생성
    cv2.namedWindow('Camera Controls')
    cv2.createTrackbar('Zoom', 'Camera Controls', 50, 100, zoom_bar)
    cv2.createTrackbar('Focus', 'Camera Controls', 0, 20, focus_bar)
    
    # 녹화 관련 변수
    recording = False
    out = None
    start_time = None
    
    print("'4'키를 눌러 녹화 시작, 'B'키를 눌러 종료합니다.")
    print(f"영상은 {os.path.abspath(save_dir)} 폴더에 저장됩니다.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("카메라에서 프레임을 읽을 수 없습니다.")
            break
            
        # 좌우 반전 (거울 효과)
        frame = cv2.flip(frame, 1)
        
        # 이미지 처리
        h, w = frame.shape[:2]
        
        # 줌 효과 적용
        if zoom_factor > 1.0:
            center_x, center_y = w//2, h//2
            new_w = int(w/zoom_factor)
            new_h = int(h/zoom_factor)
            x1 = center_x - new_w//2
            y1 = center_y - new_h//2
            x2 = center_x + new_w//2
            y2 = center_y + new_h//2
            frame = frame[y1:y2, x1:x2]
            frame = cv2.resize(frame, (w, h))
        
        # 초점 효과 적용 (블러)
        if blur_factor > 0:
            ksize = blur_factor * 2 + 1
            if ksize > 1:
                frame = cv2.GaussianBlur(frame, (ksize, ksize), 0)
        
        # 녹화 중일 때 시간 표시
        if recording:
            elapsed_time = time.time() - start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            time_text = f"Recording: {minutes:02d}:{seconds:02d}"
            cv2.putText(frame, time_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            out.write(frame)
        
        # 화면에 현재 상태와 설정값 표시
        status = "Recording" if recording else "Press '4' to start recording"
        cv2.putText(frame, status, (10, frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"zoom: {zoom_factor:.1f}x", (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"focus: {blur_factor}", (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 화면 표시
        cv2.imshow('Camera', frame)
        
        # 키 입력 처리
        key = cv2.waitKey(1) & 0xFF
        
        if key == 52:  # 4키
            if not recording:
                # 파일명 생성
                filename = os.path.join(save_dir, f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
                # 코덱 설정 (H.264)
                fourcc = cv2.VideoWriter_fourcc(*'avc1')
                # VideoWriter 객체 생성
                out = cv2.VideoWriter(filename, fourcc, 30.0, (1920, 1080))
                if not out.isOpened():
                    print("비디오 파일을 생성할 수 없습니다.")
                    continue
                recording = True
                start_time = time.time()
                print(f"녹화 시작: {filename}")
            else:
                print("이미 녹화 중입니다.")
        
        elif key == 66:  # B키
            if recording:
                out.release()
                print("녹화 종료")
            print("프로그램을 종료합니다.")
            break
    
    # 정리
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()