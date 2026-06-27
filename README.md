# Drowsiness Detection System
### L&T EduTech — Microcontroller Based Industrial Applications


## 1. Problem Statement

Driver drowsiness is a major cause of road accidents worldwide. According to the National Highway Traffic Safety Administration (NHTSA), drowsy driving accounts for approximately 100,000 police-reported crashes annually. Existing solutions are either too expensive (camera-integrated ECUs), require additional hardware purchase, or have high latency. This project proposes a hybrid edge-host architecture where a laptop webcam performs real-time Eye Aspect Ratio (EAR) based drowsiness detection and alerts the driver via an ESP32 microcontroller controlling LEDs and a buzzer — using zero additional hardware cost beyond what a developer already owns.

---

## 2. Scope of the Solution

- **Detection method:** EAR (Eye Aspect Ratio) algorithm using dlib 68-point facial landmark model on laptop webcam
- **Alert mechanism:** ESP32 drives Red LED (alert) + Buzzer (audible alarm) via USB serial commands from host Python
- **States:** ALERT (green LED) → WARNING (red blink + short beep) → DROWSY (red steady + continuous buzzer)
- **Simulation:** Wokwi-based simulation with push button to toggle states (camera unavailable in Wokwi)
- **Scope exclusions:** GPS integration, GSM alerting, and cloud logging are out of scope

---

## 3. Architecture of the solution

<img width="843" height="622" alt="image" src="https://github.com/user-attachments/assets/d4875654-3556-4810-b096-a1a0cc785c34" />



## 4. Code for the Solution

### 4.1 ESP32 Firmware (Arduino C++)
See `esp32_drowsiness.ino` .

**Key logic:**
- `Serial.read()` parses single-byte command: `'D'`, `'A'`, or `'W'`
- GPIO HIGH/LOW drives LEDs and active buzzer
- Self-test on boot (all peripherals blink/beep once)

### 4.2 Python Host (EAR Algorithm)
See `drowsiness_host.py` in GitHub repository.

**EAR Formula:**
```
          ||p2-p6|| + ||p3-p5||
EAR =  ─────────────────────────
              2 × ||p1-p4||
```

Where p1–p6 are the 6 eye landmark points from dlib's 68-point model.

- EAR < 0.25 for 10+ frames → WARNING (`'W'`)
- EAR < 0.25 for 20+ frames → DROWSY (`'D'`)
- EAR ≥ 0.25 after drowsy → ALERT (`'A'`)

---

## 5. Results of Simulation

### Wokwi Simulation Results

| Button Press | State    | Green LED | Red LED | Buzzer |
|--------------|----------|-----------|---------|--------|
| 0 (default)  | ALERT    | ON        | OFF     | OFF    |
| 1 (press)    | DROWSY   | OFF       | ON      | ON     |
| 2 (press)    | ALERT    | ON        | OFF     | OFF    |

Serial Monitor output:
```
ESP32 Drowsiness Alert Ready
SIMULATED: DRIVER ALERT
SIMULATED: DROWSY DETECTED
SIMULATED: DRIVER ALERT
```

### Python + Webcam Results
- EAR value range when eyes open: **0.28 – 0.35**
- EAR value range when eyes closed: **0.01 – 0.12**
- Detection latency: **< 200ms** (20 frames @ ~30fps)
- False positive rate: minimal under adequate lighting

---


## 6. Video of the Demo (Prototype)

Video demonstrating:
1. Python script running on laptop detecting open/closed eyes via webcam
2. Serial commands being sent to ESP32
3. Green LED → Red LED + Buzzer transition on drowsiness detection

**Video Link:** https://drive.google.com/file/d/1n0hNS0R_YoxeVFXQ7voELo-CGKAu_B7I/view?usp=drive_link

---

## 7. References

1. Soukupová, T., & Čech, J. (2016). *Real-time eye blink detection using facial landmarks*. In 21st Computer Vision Winter Workshop (CVWW).

2. King, D. E. (2009). *Dlib-ml: A machine learning toolkit*. Journal of Machine Learning Research, 10, 1755–1758. https://doi.org/10.5555/1577069.1755839

3. Bradski, G. (2000). *The OpenCV Library*. Dr. Dobb's Journal of Software Tools. https://opencv.org/

4. Espressif Systems. (2023). *ESP32 Technical Reference Manual v5.1*. https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf

5. National Highway Traffic Safety Administration. (2017). *Drowsy Driving*. U.S. Department of Transportation. https://www.nhtsa.gov/risky-driving/drowsy-driving

6. Rosebrock, A. (2017). *Drowsiness detection with OpenCV*. PyImageSearch. https://www.pyimagesearch.com/2017/05/08/drowsy-driver-detection-opencv/

7. Arduino / Espressif. (2023). *Arduino core for ESP32*. GitHub. https://github.com/espressif/arduino-esp32

8. Wokwi. (2024). *ESP32 Online Simulator*. https://wokwi.com/

9. Circuit Digest. (2022). *Arduino Based Driver Drowsiness Detection and Alert System*. https://circuitdigest.com/microcontroller-projects/arduino-based-driver-drowsiness-detection-and-alert-system

10. EasyEDA. (2024). *Online PCB Design Tool*. https://easyeda.com/
