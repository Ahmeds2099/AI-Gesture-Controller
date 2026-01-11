____________________________` AI Gesture Controller (Precision Edition) `________________________________________________ 
This document outlines the setup and operation of my gesture-based control system. We have transitioned from simple tracking to a State-Based AI Architecture to ensure every movement is intentional and precise.

__________________________________________` 🛠 Project Evolution & Logic `________________________________________________
To achieve professional-grade precision, we implemented several advanced logic layers:

[!TIP] `Mode State Machine:` The system operates in distinct states (Navigation, Scroll, Volume, Grab). This prevents overlapping commands—ensuring, for example, that you don't accidentally scroll while trying to move the mouse.

[!IMPORTANT] `Master-Index Anchoring:`The Index finger is the "anchor." If the index finger is not in the correct position, the AI ignores other finger movements, virtually eliminating "ghost" clicks.

[!WARNING] `The Brake-Buffer (1.0s):` We solved cursor "jitter" by creating a 1-second freeze buffer. When the thumb stretches, the cursor locks instantly, giving you a stable window to click without the mouse drifting.

[!NOTE] `Pulse-Trigger Grab:` Distinguishes "Pinching" from "Grabbing" via timing. A Grab only activates if the hand goes from Fully Open to a Fist in under 0.4 seconds.

_______________________________________________`⚙️ Setup Instructions`____________________________________________________
>1.Requirements
Python 3.8+
Standard USB or Integrated Webcam

>2. Install Dependencies`
Open your terminal (Command Prompt or PowerShell) and run:

Bash
`pip install opencv-python mediapipe pyautogui numpy`

>3. Running the Application
Navigate to your script folder and execute:

Bash
`python run_app.py`

______________________________________________`🖐️ Gesture Instruction Manual`____________________________________________
`1. Standard Mouse Mode (Default)`
Move Cursor: Point with your Index Finger. The cursor maps 1:1 to your camera view.
Freeze Cursor (The Brake): Stretch your Thumb out (L-shape).

`Visual Cue:` The line on screen turns <span style="color:green">Green</span> then <span style="color:yellow">Yellow</span>, indicating the cursor is LOCKED.
Left Click: While the cursor is Frozen, pinch your Index and Thumb together.

`2. Grab & Drag Mode`
To Enter: Quickly close your hand into a Fist and release (Pulse gesture). The screen will display "GRAB MODE ACTIVE."

To Drag:
Point at the item.
Stretch Thumb to freeze the cursor.
Pinch fingers to "Grab" (MouseDown).
Tuck thumb back in to move the item.
To Release: Pinch again or open your hand wide.

`3. Utility Modes (Hold for 1 Second)`
Scroll Mode: Hold 2 fingers (Index + Middle) up. Tilt hand Up/Down to scroll.
Volume Mode: Hold 3 fingers up. Tilt hand Up/Down to adjust volume.

[!NOTE] A Green Progress Bar will appear while the AI "scans" your hand to confirm the mode change.

`4. Global Reset`
Open Palm: Spread all 4 fingers wide at any time. This acts as an "Emergency Stop" to clear any mode and return to Standard Navigation.

________________________________________________`💻 Terminal Feedback`____________________________________________________
Upon launching, the terminal will display a Quick-Reference Guide so you can operate the system without keeping this document open.