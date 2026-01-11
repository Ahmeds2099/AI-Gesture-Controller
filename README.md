# AI-Driven Gesture Control System

A high-precision computer vision application that translates real-time hand landmarks into system-level mouse and keyboard events.

## Features
- **Precision Tracking:** Uses Index-Tip tracking with exponential smoothing to eliminate sensor noise.
- **Gesture Suite:** - **Pinch:** Left Click (with cursor-lock to prevent drift).
  - **Fist:** Grab and Drag functionality.
  - **V-Sign:** Velocity-based smooth scrolling.
- **Full Screen Mapping:** Maps camera coordinates directly to monitor resolution.

## Tech Stack
- **Language:** Python
- **Libraries:** OpenCV, MediaPipe, PyAutoGUI, NumPy
- **Deployment:** Windows Batch Scripting

## Installation & Usage
1. Clone the repository.
2. Run the `start_ai_mouse.bat` file to automatically set up the environment and launch the application.
3. Press 'q' to exit the camera feed.