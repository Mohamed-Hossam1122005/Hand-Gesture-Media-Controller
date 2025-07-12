import cv2
import streamlit as st
import mediapipe as mp
import pyautogui
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def count_fingers(lst):
    cnt = 0
    thresh = (lst.landmark[0].y*100 - lst.landmark[9].y*100)/2

    if (lst.landmark[5].y*100 - lst.landmark[8].y*100) > thresh:
        cnt += 1
    if (lst.landmark[9].y*100 - lst.landmark[12].y*100) > thresh:
        cnt += 1
    if (lst.landmark[13].y*100 - lst.landmark[16].y*100) > thresh:
        cnt += 1
    if (lst.landmark[17].y*100 - lst.landmark[20].y*100) > thresh:
        cnt += 1
    if (lst.landmark[5].x*100 - lst.landmark[4].x*100) > 6:
        cnt += 1
    return cnt

st.set_page_config(page_title="Hand Gesture Media Controller", layout="centered")
st.title("Hand Gesture Media Controller")
st.markdown(
    """
    This application uses your webcam to detect hand gestures and control media playback 
    in real-time.

    **How to use:**
    - Raise your hand in front of the webcam.
    - Different number of fingers trigger different media actions:
        - **1 finger**: Next (Right Arrow)
        - **2 fingers**: Previous (Left Arrow)
        - **3 fingers**: Volume Up (Up Arrow)
        - **4 fingers**: Volume Down (Down Arrow)
        - **5 fingers**: Play/Pause (Spacebar)
    - Click the button below to start your webcam.
    """
)

start_button = st.button("Start Webcam")

if start_button:
    stframe = st.empty()
    cap = cv2.VideoCapture(0)

    prev = -1
    start_init = False
    start_time = 0

    with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.error("Unable to access the webcam.")
                break

            end_time = time.time()
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb_frame)

            if result.multi_hand_landmarks:
                hand_landmarks = result.multi_hand_landmarks[0]
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                cnt = count_fingers(hand_landmarks)
                cv2.putText(frame, f'Fingers: {cnt}', (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                if cnt != prev:
                    if not start_init:
                        start_time = time.time()
                        start_init = True
                    elif (end_time - start_time) > 0.2:
                        if cnt == 1:
                            pyautogui.press("right")
                        elif cnt == 2:
                            pyautogui.press("left")
                        elif cnt == 3:
                            pyautogui.press("up")
                        elif cnt == 4:
                            pyautogui.press("down")
                        elif cnt == 5:
                            pyautogui.press("space")
                        prev = cnt
                        start_init = False

            stframe.image(frame, channels="BGR")
        cap.release()
