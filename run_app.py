import sys
import os
import cv2
import numpy as np
import pyautogui
import math

# --- 1. SETTINGS ---
screen_w, screen_h = pyautogui.size()
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# Smoothing & State
smoothening = 5 
plocX, plocY = 0, 0
dragging = False 
clicked = False

# --- 2. IMPORT MEDIAPIPE ---
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
except Exception as e:
    print(f"Error: {e}")
    sys.exit()

detector = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
cap = cv2.VideoCapture(0)

cv2.namedWindow("Pinch Precision Control", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Pinch Precision Control", 1080, 720)

while cap.isOpened():
    success, img = cap.read()
    if not success: break

    img = cv2.flip(img, 1)
    h, w, c = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = detector.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            lms = hand_lms.landmark
            
            # --- LANDMARKS ---
            t_tip = lms[4]  # Thumb Tip
            i_tip = lms[8]  # Index Tip
            m_tip = lms[12] # Middle Tip
            r_tip = lms[16] # Ring Tip

            # --- COORDINATE MAPPING ---
            ix, iy = int(i_tip.x * w), int(i_tip.y * h)
            x3 = np.interp(ix, (0, w), (0, screen_w))
            y3 = np.interp(iy, (0, h), (0, screen_h))
            
            currX = plocX + (x3 - plocX) / smoothening
            currY = plocY + (y3 - plocY) / smoothening

            # --- GESTURE CALCULATIONS ---
            idx_up = i_tip.y < lms[6].y
            mid_up = m_tip.y < lms[10].y
            rng_up = r_tip.y < lms[14].y
            
            # Distance between Index and Thumb
            dist_pinch = math.hypot(int(i_tip.x*w) - int(t_tip.x*w), int(i_tip.y*h) - int(t_tip.y*h))

            # --- 3. ACTION LOGIC ---

            # A. SCROLLING (Index + Middle UP, Ring DOWN)
            # This specific check prevents "Grab" from triggering during scroll
            if idx_up and mid_up and not rng_up:
                cv2.putText(img, "SCROLLING", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                diff = plocY - currY
                if abs(diff) > 10:
                    pyautogui.scroll(int(diff * 2)) # Multiplier for smoothness
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False

            # B. GRAB / DRAG (Full Fist - All fingers folded)
            elif not idx_up and not mid_up and not rng_up:
                if not dragging:
                    pyautogui.mouseDown()
                    dragging = True
                cv2.putText(img, "GRABBED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                pyautogui.moveTo(currX, currY)

            # C. PINCH CLICK & IDLE MOVEMENT
            else:
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False
                
                # If we are starting to pinch (distance < 40)
                if dist_pinch < 40:
                    # DRAW A LINE between fingers to show pinch is active
                    tx, ty = int(t_tip.x * w), int(t_tip.y * h)
                    cv2.line(img, (ix, iy), (tx, ty), (0, 255, 0), 3)
                    
                    if dist_pinch < 30: # Final click threshold
                        if not clicked:
                            pyautogui.click()
                            clicked = True
                    # IMPORTANT: We do NOT update pyautogui.moveTo here.
                    # This "freezes" the mouse during the pinch to stop the drop.
                else:
                    clicked = False
                    pyautogui.moveTo(currX, currY)
                
                cv2.circle(img, (ix, iy), 10, (255, 0, 255), cv2.FILLED)

            plocX, plocY = currX, currY
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Pinch Precision Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()