import sys
import cv2
import numpy as np
import pyautogui
import math
import time

def print_instructions():
    """Prints clear usage guide to the terminal on startup"""
    print("\n" + "="*60)
    print("         🚀 PRECISION GESTURE CONTROLLER STARTING...")
    print("="*60)
    print("\n[MOUSE CONTROL]")
    print("  • MOVE: Point with INDEX finger.")
    print("  • FREEZE (Brake): Stretch THUMB out away from palm.")
    print("  • CLICK: While Frozen, PINCH Index and Thumb together.")
    print("\n[GRAB & DRAG]")
    print("  • TRIGGER: Quickly close your hand into a FIST (Open -> Close).")
    print("  • ACTION: Point -> Stretch Thumb (Freeze) -> Pinch to Grab.")
    print("\n[SPECIAL MODES]")
    print("  • SCROLL: Hold 2 fingers up (1 second).")
    print("  • VOLUME: Hold 3 fingers up (1 second).")
    print("\n[SAFETY]")
    print("  • RESET: Spread ALL 4 FINGERS wide to return to Mouse Mode.")
    print("  • EXIT: Press 'Q' on the video window to quit.")
    print("="*60 + "\n")

# --- 1. INITIAL SETTINGS ---
screen_w, screen_h = pyautogui.size()
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# Movement Smoothing
smoothening = 5
plocX, plocY = 0, 0
dragging = False 
clicked = False
current_mode = 0 # 0:Mouse, 1:Scroll, 2:Volume, 3:Grab

# Gesture Timers
gesture_start_time = 0
last_detected_up_count = -1
REQUIRED_HOLD_TIME = 1.0 

# Brake/Buffer Logic
brake_active = False
brake_lock_expiry = 0
BRAKE_GRACE_PERIOD = 1.0
THUMB_STRETCH_THRESHOLD = 0.08

# Grab Pulse Logic
last_open_time = 0
grab_pulse_ready = False

# --- 2. STARTUP ---
print_instructions()

try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
except Exception as e:
    print(f"ERROR: Missing libraries. Run: pip install mediapipe opencv-python pyautogui")
    sys.exit()

detector = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# --- 3. MAIN LOOP ---
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
            
            # Landmark Shortcuts
            t_tip, i_base, i_tip = lms[4], lms[5], lms[8]
            m_tip, r_tip, p_tip = lms[12], lms[16], lms[20]

            # Coordinate Mapping (Index Finger Anchor)
            margin = 120 
            fx, fy = i_tip.x * w, i_tip.y * h
            tx = np.interp(fx, (margin, w - margin), (0, screen_w))
            ty = np.interp(fy, (margin, h - margin), (0, screen_h))
            currX = plocX + (tx - plocX) / smoothening
            currY = plocY + (ty - plocY) / smoothening

            # Finger Counting
            idx_up = i_tip.y < lms[6].y
            mid_up = m_tip.y < lms[10].y
            rng_up = r_tip.y < lms[14].y
            pnk_up = p_tip.y < lms[18].y
            up_count = [idx_up, mid_up, rng_up, pnk_up].count(True)

            # BRAKE LOGIC (Check for Thumb Stretch)
            thumb_gap = abs(t_tip.x - i_base.x)
            real_time_thumb_away = (thumb_gap > THUMB_STRETCH_THRESHOLD) and up_count > 0
            
            if real_time_thumb_away:
                brake_active = True
                brake_lock_expiry = time.time() + BRAKE_GRACE_PERIOD
            elif time.time() > brake_lock_expiry:
                brake_active = False

            # GRAB PULSE LOGIC (Open hand -> Fist quickly)
            if up_count == 4:
                grab_pulse_ready = True
                last_open_time = time.time()
                current_mode = 0 # Auto-reset to mouse on open palm
                if dragging:
                    pyautogui.mouseUp()
                    dragging = False
            
            if grab_pulse_ready and up_count == 0:
                if (time.time() - last_open_time) < 0.4:
                    current_mode = 3 # Enter Grab Mode
                    grab_pulse_ready = False
                    brake_active = False

            # GESTURE LOCKING (Scroll/Volume)
            if up_count != last_detected_up_count:
                gesture_start_time = time.time()
                last_detected_up_count = up_count
            hold_duration = time.time() - gesture_start_time

            if current_mode == 0 and up_count in [2, 3]:
                if hold_duration > REQUIRED_HOLD_TIME:
                    current_mode = 1 if up_count == 2 else 2

            # EXECUTION
            dist_pinch = math.hypot(int(i_tip.x*w) - int(t_tip.x*w), int(i_tip.y*h) - int(t_tip.y*h))
            
            # Draw Status Line
            line_color = (0, 255, 0) if real_time_thumb_away else (0, 255, 255) if brake_active else (0, 0, 255)
            cv2.line(img, (int(t_tip.x*w), int(t_tip.y*h)), (int(i_base.x*w), int(i_base.y*h)), line_color, 2)

            # Mode Actions
            if current_mode == 0: # MOUSE
                if up_count == 1:
                    if brake_active:
                        cv2.putText(img, "FROZEN (Ready to Click)", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        if dist_pinch < 35:
                            if not clicked:
                                pyautogui.click()
                                clicked = True
                                brake_lock_expiry = 0
                        else: clicked = False
                    else:
                        cv2.putText(img, "MOUSE ACTIVE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
                        pyautogui.moveTo(currX, currY)
            
            elif current_mode == 3: # GRAB
                cv2.putText(img, "GRAB MODE LOCKED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                if idx_up:
                    if brake_active:
                        if dist_pinch < 35:
                            if not dragging:
                                pyautogui.mouseDown()
                                dragging = True
                        else:
                            if dragging:
                                pyautogui.mouseUp()
                                dragging = False
                    else:
                        pyautogui.moveTo(currX, currY)

            # Visual Scanning Bar
            if current_mode == 0 and up_count in [2, 3]:
                prog_w = int((hold_duration / REQUIRED_HOLD_TIME) * 300)
                cv2.rectangle(img, (50, 120), (350, 140), (40, 40, 40), -1)
                cv2.rectangle(img, (50, 120), (50 + min(prog_w, 300), 140), (0, 255, 0), -1)

            plocX, plocY = currX, currY
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()