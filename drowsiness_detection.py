"""
Drowsiness Detection System — Python Host (Laptop Webcam)
Uses: OpenCV + dlib + scipy for Eye Aspect Ratio (EAR)
Sends serial commands to ESP32 via USB(UART)
"""

import cv2
import dlib
import serial
import argparse
import time
from scipy.spatial import distance as dist
from imutils import face_utils
import imutils

# ─── TUNABLE PARAMETERS
EAR_THRESHOLD   = 0.25   # Below this eyes considered closed
WARNING_THRESH  = 0.28   # Between this and EAR_THRESHOLD warning zone
CONSEC_FRAMES   = 20     # Frames eye must be closed to trigger DROWSY alert
WARNING_FRAMES  = 10     # Frames to trigger WARNING
SERIAL_PORT     = None   # Set via --port argument
BAUD_RATE       = 115200


# Landmark indices for left and right eye (dlib 68-point model)
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


def eye_aspect_ratio(eye):
    """Compute Eye Aspect Ratio (EAR).
    EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    When eye is open EAR ≈ 0.3; when closed EAR ≈ 0.0
    """
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)


def send_command(ser, cmd, last_cmd):
    #Send command to ESP32 only if state changed (avoid flooding serial)
    if cmd != last_cmd:
        if ser:
            ser.write(cmd.encode())
        print(f"[SERIAL → ESP32] {cmd}")
    return cmd


def main(port):
    
    ser = None
    if port:
        try:
            ser = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2)  # Wait for ESP32 to reset
            print(f"[OK] Connected to ESP32 on {port}")
        except Exception as e:
            print(f"[WARN] Serial connection failed: {e}")
            print("[INFO] Running in webcam-only mode (no ESP32)")

    #dlib face detector and landmark predictor
    print("[INFO] Loading face detector...")
    detector  = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    #Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam. Check camera index.")
        return

    frame_counter = 0
    last_cmd      = ""
    state         = "ALERT"

    print("[INFO] System running. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = imutils.resize(frame, width=640)
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye  = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]

            leftEAR  = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear      = (leftEAR + rightEAR) / 2.0

            # Draw eye contours
            cv2.drawContours(frame, [cv2.convexHull(leftEye)],  -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [cv2.convexHull(rightEye)], -1, (0, 255, 0), 1)

            #State machine
            if ear < EAR_THRESHOLD:
                frame_counter += 1

                if frame_counter >= CONSEC_FRAMES:
                    state    = "DROWSY"
                    last_cmd = send_command(ser, "D", last_cmd)
                    cv2.putText(frame, "*** DROWSY! WAKE UP! ***",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                elif frame_counter >= WARNING_FRAMES:
                    state    = "WARNING"
                    last_cmd = send_command(ser, "W", last_cmd)
                    cv2.putText(frame, "WARNING: Eyes Closing",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            else:
                if frame_counter > 0:
                    # Eyes reopened
                    state    = "ALERT"
                    last_cmd = send_command(ser, "A", last_cmd)
                frame_counter = 0

            # ── HUD ──────────────────────────────────────────────────────
            cv2.putText(frame, f"EAR: {ear:.3f}", (480, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(frame, f"State: {state}", (480, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 255, 0) if state == "ALERT" else (0, 0, 255), 2)
            cv2.putText(frame, f"Frames: {frame_counter}", (480, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow("Drowsiness Detection — EAR System", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    if ser:
        ser.write(b'A')   # Reset ESP32 to ALERT state on exit
        ser.close()
    print("[INFO] Exited cleanly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Drowsiness Detection Host")
    parser.add_argument("--port", type=str, default=None,
                        help="Serial port of ESP32 (e.g., COM3 or /dev/ttyUSB0)")
    args = parser.parse_args()
    main(args.port)