# Smart-Study-Monitor 🎓

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red.svg)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange.svg)](https://developers.google.com/mediapipe)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-yellow.svg)](https://docs.ultralytics.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

Smart Study Monitor is an AI-powered system that uses computer vision to monitor student focus in real time. It detects drowsiness, eye movement, phone usage, and face obstruction, providing instant alerts. Built with Python, OpenCV, MediaPipe, YOLOv8, Scikit-Learn, and FastAPI, it helps students build better and more productive study habits.

---

## 🌟 Features

* 👁️ **Eye & Attention Monitoring** — MediaPipe Face Mesh tracks eye movement, gaze direction (screen, down, away), and computes Eye Aspect Ratio (EAR) for blink rate and micro-sleep detection.
* 😴 **Drowsiness Detection** — Identifies prolonged eye closure and head drops, triggering motivational wake-up alerts.
* 📱 **Phone Detection** — Real-time YOLOv8 object detection with temporal persistence filters to eliminate false positives.
* 🚫 **Face Obstruction Detection** — Differentiates between normal book reading and intentionally hiding the face behind books or objects.
* 🧘 **Posture & Ergonomics** — MediaPipe Pose analyzes shoulder tilt and spinal slouching to protect student ergonomics.
* 🤖 **Hybrid ML Decision Engine** — Fuses deterministic safety invariants with a 14-dimensional trained ML behavioral classifier and personalized adaptive baselines.
* 🔊 **Spoken Hindi Voice Alerts** — Spoken voice alarms in natural Hindi for Drowsiness (*"उठ जा! उठ जा! उठ रे!"*), Face Obstruction (*"बाबू कोई नहीं देख रहा है, मुँह दिखाओ।"*), and Phone Distraction (*"तुम एक काम करो, IAS की तैयारी छोड़ दो..."*) with smart priority preemption and a 5-second cooldown.
* 📊 **Study Insights & Persistence** — SQLite database records study history, focus streaks, distraction episodes, and average recovery times.
* 🌐 **FastAPI REST & WebSocket Backend** — High-performance backend streaming live JSON telemetry over WebSocket to interactive dashboards.
* 💻 **Interactive Live Dashboard** — Built-in dashboard served directly at `http://127.0.0.1:8000/dashboard` with live scores, timers, and event timeline.

---

## 🛠️ Tech Stack

* **Language**: Python 3.10 – 3.13
* **Computer Vision**: OpenCV, MediaPipe Face Mesh, MediaPipe Pose
* **Deep Learning & ML**: YOLOv8 (Ultralytics), Scikit-Learn, Joblib, NumPy
* **Audio System**: Pygame Mixer (Local 44.1kHz Stereo PCM WAV playback)
* **Backend API & WebSockets**: FastAPI, Uvicorn, WebSockets, AnyIO
* **Database**: SQLite3 with repository pattern
* **Frontend**: Vanilla JS / HTML5 Dashboard (Single-host) & Next.js

---

## 🏗️ System Overview

```text
                  CAMERA FEED
                       │
                       ▼
               PERCEPTION LAYER
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   FACE / EYES    YOLO (Objects)     POSE
   (Mesh + Gaze)  (Phone & Book)   (Posture)
        │              │              │
        └──────────────┼──────────────┘
                       ▼
               FEATURE FUSION (14-D Vector)
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
   DETERMINISTIC RULES          ML BEHAVIOR MODEL
   (Safety Invariants)         (Trained Classifier)
        │                             │
        └──────────────┬──────────────┘
                       ▼
                TEMPORAL ENGINE (Persistence Window)
                       │
                BEHAVIOR ENGINE (Study State Machine)
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  SESSION MANAGER  EVENT BUS      FOCUS SCORER
  (SQLite DB)          │          (0-100% Score)
                       ▼
              ┌─────────────────┐
              │  ALERT MANAGER  │
              └────────┬────────┘
             ┌─────────┴─────────┐
             ▼                   ▼
      SCREEN OVERLAY        AUDIO PLAYER
     (High-Contrast)       (Local Hindi WAV)
             │
             ▼
      FASTAPI SERVER (REST + WebSockets)
             │
             ▼
     LIVE WEB DASHBOARD (http://127.0.0.1:8000/dashboard)
```

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Amankumarsingh355/Smart-Study-Monitor.git
cd Smart-Study-Monitor
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows PowerShell**:
  ```powershell
  .\venv\Scripts\activate
  ```
- **Linux / macOS**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

Start the **Unified System** (FastAPI Backend + OpenCV AI Engine + Live Web Dashboard):

```bash
python run_smart_study_monitor.py
```
*(Or double-click `run.bat` on Windows)*

- **Live Web Dashboard**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Interactive REST API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Exit & Save Session**: Press **`q`** in the OpenCV camera window or **`Ctrl + C`** in terminal.

#### Modular Startup Options
```bash
# Run FastAPI Backend only
python run_smart_study_monitor.py --backend

# Run Computer Vision AI Perception Loop only
python run_smart_study_monitor.py --camera
```

---

## 🧪 Testing

Execute the comprehensive automated test suite (107 unit and integration tests):
```bash
pytest
```

---

## 📁 Project Structure

```text
Smart-Study-Monitor/
├── app.py                      # Main computer vision perception loop
├── config.py                   # Centralized application & alert configuration
├── run_smart_study_monitor.py  # Unified launcher (FastAPI + Vision + Dashboard)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container deployment configuration
├── docker-compose.yml          # Multi-service container orchestration
├── assets/
│   └── sounds/                 # Local Hindi spoken WAV alert files
├── backend/
│   ├── main.py                 # FastAPI application root & routers
│   ├── static/                 # Static live web dashboard (index.html)
│   ├── websocket/              # WebSocket manager and event bus forwarder
│   └── services/               # Session & analytics business services
├── dashboard/                  # Optional Next.js frontend application
├── ml_training/                # Dataset generation, training & evaluation pipelines
├── models/                     # Serialized ML models and landmark tasks
├── scripts/                    # Offline asset generation utilities
├── src/
│   ├── alerts/                 # AudioPlayer and AlertManager
│   ├── behavior/               # Temporal engine, feature fusion, state machine
│   ├── camera/                 # OpenCV frame capture and camera manager
│   ├── database/               # SQLite schema and session repository
│   ├── detection/              # YOLOv8 object detection wrapper
│   ├── events/                 # Pub/Sub event bus
│   ├── face/                   # Face mesh and eye EAR analyzer
│   ├── gaze/                   # Iris direction and gaze vector tracker
│   ├── ml/                     # Feature extractor, predictor, personalization
│   ├── pose/                   # MediaPipe pose & ergonomic posture analyzer
│   └── session/                # Study session manager and metrics calculator
└── tests/                      # 107 automated pytest test cases
```

---

## 🎯 Objective

The goal of Smart Study Monitor is to create an intelligent, unobtrusive study companion that helps students recognize distractions and fatigue in real time, encouraging sustained deep work, ergonomic posture, and long-term academic excellence.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Aman Kumar Singh**
GitHub: [@Amankumarsingh355](https://github.com/Amankumarsingh355)
