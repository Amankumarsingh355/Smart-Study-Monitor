# Smart-Study-Monitor
Smart Study Monitor is an AI-powered system that uses computer vision to monitor student focus in real time. It detects drowsiness, eye movement, phone usage, and face obstruction, providing instant alerts. Built with Python, OpenCV, MediaPipe/cvzone, YOLO and FastAPI, it helps students build better and more productive study habits.

## Features

* 👁️ **Eye & Attention Monitoring** — Tracks eye movement and signs of reduced attention.
* 😴 **Drowsiness Detection** — Detects prolonged eye closure and potential fatigue.
* 📱 **Phone Detection** — Uses YOLO-based object detection to identify phone usage.
* 🚫 **Face Obstruction Detection** — Detects when the face is partially or completely obstructed.
* 🔔 **Real-Time Alerts** — Provides alerts when distraction or drowsiness is detected.
* 📊 **Study Insights** — Helps analyze study sessions and identify focus patterns.
* 🌐 **Backend API** — FastAPI-based backend for processing and serving monitoring data.

## Tech Stack

* **Python**
* **OpenCV**
* **MediaPipe / cvzone**
* **YOLO**
* **Pygame**
* **FastAPI**
* **Next.js** *(for dashboard, if enabled)*

## System Overview

```text
Camera
   ↓
Video Frames
   ↓
Computer Vision Processing
   ├── Face & Eye Monitoring
   ├── Drowsiness Detection
   ├── Phone Detection
   └── Face Obstruction Detection
   ↓
Event / Alert Detection
   ↓
Real-Time Alerts
   ↓
Study Monitoring Dashboard
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Amankumarsingh355/Smart-Study-Monitor.git
cd Smart-Study-Monitor
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

Follow the project-specific backend/frontend instructions provided in the repository.

## Project Structure

```text
Smart-Study-Monitor/
│
├── backend/
├── frontend/
├── models/
├── assets/
├── requirements.txt
├── README.md
└── LICENSE
```

## Objective

The goal of Smart Study Monitor is to create an intelligent study environment that helps students recognize distractions and fatigue while studying, allowing them to improve their concentration and study efficiency.

## Future Improvements

* Personalized focus analytics
* Study-session history
* Productivity scoring
* Advanced fatigue detection
* Cloud-based analytics
* Mobile application
* AI-generated study recommendations

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## Author

**Aman Kumar Singh**

GitHub: [@Amankumarsingh355](https://github.com/Amankumarsingh355)
