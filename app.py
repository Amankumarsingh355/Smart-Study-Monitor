import cv2
import time

from config.settings import default_config
from src.camera.camera_manager import CameraManager
from src.face.face_mesh import FaceMeshDetector
from src.face.eye_analyzer import EyeAnalyzer
from src.detection.object_detector import ObjectDetector
from src.pose.pose_detector import PoseDetector
from src.pose.posture_analyzer import PostureAnalyzer
from src.gaze.gaze_analyzer import GazeAnalyzer
from src.behavior.temporal_engine import TemporalEngine
from src.behavior.feature_fusion import FeatureFusion
from src.behavior.study_state import StudyState, StudyStateEngine
from src.ml import HybridStudyStateEngine
from src.behavior.focus_scorer import FocusScorer
from src.behavior.behavior_history import BehaviorHistory
from src.behavior.session_metrics import SessionMetrics
from src.database.database import DatabaseManager
from src.database.repository import SessionRepository
from src.session.session_manager import SessionManager
from src.alerts.alert_manager import AlertManager


def main():

    cfg = default_config

    camera = CameraManager(
        camera_index=cfg.camera.camera_index,
        width=cfg.camera.width,
        height=cfg.camera.height
    )

    face_detector = FaceMeshDetector(
        max_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    eye_analyzer = EyeAnalyzer()

    object_detector = ObjectDetector(
        model_name="yolov8n.pt",
        target_classes=["cell phone", "book"]
    )

    pose_detector = PoseDetector()
    posture_analyzer = PostureAnalyzer()
    gaze_analyzer = GazeAnalyzer()

    # Temporal & Behavioral Engine Subsystems
    temporal_engine = TemporalEngine()
    feature_fusion = FeatureFusion()
    study_state_engine = HybridStudyStateEngine(debounce_frames=3)
    focus_scorer = FocusScorer()
    behavior_history = BehaviorHistory(max_samples=600)
    session_metrics = SessionMetrics()

    # Database & Session Persistence
    db_manager = DatabaseManager(db_path=cfg.database.db_path)
    session_repo = SessionRepository(db_manager)
    session_manager = SessionManager(
        repository=session_repo,
        sample_interval_seconds=cfg.database.sample_interval_seconds
    )

    alert_manager = AlertManager(
        cooldown_seconds=cfg.alert.cooldown_seconds
    )

    # Stride counters to balance CPU performance
    frame_count = 0
    yolo_stride = 4
    pose_stride = 2

    cached_phone_detected = False
    cached_book_detected = False
    cached_detections = []
    cached_posture = {"detected": False, "posture_score": 1.0, "is_slouching": False}
    cached_pose_landmarks = None

    last_frame_time = time.time()

    try:
        camera.start()
        active_session = session_manager.start_session()
        print(f"[INFO] Started Persistent Study Session: {active_session.id}")

        while True:
            current_time = time.time()
            dt = max(0.001, min(0.5, current_time - last_frame_time))
            last_frame_time = current_time
            frame_count += 1

            # --------------------------------
            # 1. Capture frame
            # --------------------------------
            frame = camera.read_frame()
            height, width, _ = frame.shape

            # --------------------------------
            # 2. Face Mesh & Eye Analysis
            # --------------------------------
            face_results = face_detector.process(frame)
            face_detected = False
            eye_data = None
            gaze_data = None
            landmarks = []

            if face_results.multi_face_landmarks:
                face_detected = True
                face_landmarks = face_results.multi_face_landmarks[0]
                for landmark in face_landmarks.landmark:
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    landmarks.append((x, y))

                eye_data = eye_analyzer.analyze(landmarks)
                gaze_data = gaze_analyzer.analyze(landmarks)

                # Highlight eye landmarks
                for index in [33, 133, 159, 145, 362, 263, 386, 374]:
                    x, y = landmarks[index]
                    cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)

            # --------------------------------
            # 3. Body Pose & Posture (Throttled)
            # --------------------------------
            if frame_count % pose_stride == 0:
                cached_pose_landmarks = pose_detector.process(frame)
                if cached_pose_landmarks:
                    cached_posture = posture_analyzer.analyze(cached_pose_landmarks)
                else:
                    cached_posture = {"detected": False, "posture_score": 1.0, "is_slouching": False}

            # Draw shoulder alignment wireframe
            if cached_pose_landmarks:
                l_sh = (cached_pose_landmarks[11][0], cached_pose_landmarks[11][1])
                r_sh = (cached_pose_landmarks[12][0], cached_pose_landmarks[12][1])
                sh_color = (0, 0, 255) if cached_posture.get("is_slouching") else (0, 255, 0)
                cv2.line(frame, l_sh, r_sh, sh_color, 2)
                cv2.circle(frame, l_sh, 5, sh_color, -1)
                cv2.circle(frame, r_sh, 5, sh_color, -1)

            # --------------------------------
            # 4. Object Detection (YOLO with Stride)
            # --------------------------------
            if frame_count % yolo_stride == 0:
                cached_detections = object_detector.detect_objects(
                    frame,
                    confidence_threshold=cfg.phone.confidence_threshold
                )
                cached_phone_detected = any(d["class_name"] == "cell phone" for d in cached_detections)
                cached_book_detected = any(d["class_name"] == "book" for d in cached_detections)

            # Draw object bounding boxes
            for det in cached_detections:
                x1, y1, x2, y2 = det["box"]
                c_name = det["class_name"]
                conf = det["confidence"]
                box_color = (0, 0, 255) if c_name == "cell phone" else (255, 165, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                cv2.putText(
                    frame,
                    f"{c_name}: {conf:.2f}",
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    box_color,
                    2
                )

            # --------------------------------
            # 5. Temporal Tracking
            # --------------------------------
            is_eyes_closed = (eye_data["average_ratio"] < cfg.eye.ear_threshold) if (face_detected and eye_data) else False
            is_looking_away = gaze_data.get("is_looking_away", False) if gaze_data else False
            is_slouching = cached_posture.get("is_slouching", False)
            is_face_blocked = bool(cached_book_detected and not face_detected)

            temporal_engine.update("phone", cached_phone_detected, current_time)
            temporal_engine.update("eyes_closed", is_eyes_closed, current_time)
            temporal_engine.update("no_face", not face_detected, current_time)
            temporal_engine.update("looking_away", is_looking_away, current_time)
            temporal_engine.update("poor_posture", is_slouching, current_time)
            temporal_engine.update("face_blocked", is_face_blocked, current_time)

            # --------------------------------
            # 6. Feature Fusion & Study-State
            # --------------------------------
            fused_features = feature_fusion.fuse(
                face_detected=face_detected,
                eye_data=eye_data,
                gaze_data=gaze_data,
                posture_data=cached_posture,
                phone_detected=cached_phone_detected,
                book_detected=cached_book_detected,
                temporal_engine=temporal_engine
            )

            # Debounced state evaluation
            current_study_state = study_state_engine.evaluate_fused(fused_features)
            state_confidence = study_state_engine.current_confidence

            # --------------------------------
            # 7. Persistent Session Engine Update
            # --------------------------------
            behavior_history.add(
                state=current_study_state.value,
                confidence=state_confidence
            )

            # Feeds time, records periodic timeline samples, and deduplicates event storage
            session_manager.update(
                current_state=current_study_state,
                confidence=state_confidence,
                dt=dt,
                current_time=current_time
            )

            # Instantaneous Scorer
            score = focus_scorer.calculate(
                phone_detected=(current_study_state == StudyState.PHONE_USAGE),
                drowsy=(current_study_state == StudyState.DROWSY),
                face_missing=(current_study_state in (StudyState.NO_FACE, StudyState.AWAY_FROM_DESK)),
                distracted=(current_study_state in (StudyState.DISTRACTED, StudyState.LOOKING_AWAY))
            )

            # --------------------------------
            # 8. Alert Management (Synchronized Spoken & Visual Alerts)
            # --------------------------------
            alert_event = None
            if current_study_state == StudyState.DROWSY:
                alert_event = "DROWSY"
            elif current_study_state == StudyState.PHONE_USAGE:
                alert_event = "PHONE_USAGE"
            elif current_study_state == StudyState.FACE_BLOCKED:
                alert_event = "FACE_BLOCKED"

            alert_manager.process_event(
                alert_event,
                current_time=current_time,
                confidence=state_confidence
            )

            # --------------------------------
            # 9. Phase 8 HUD Information Display
            # --------------------------------
            fps = camera.get_fps()

            # Semi-transparent overlay card for metrics
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (490, 375), (20, 20, 20), -1)
            cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

            # Title & Session ID
            cv2.putText(frame, "SMART STUDY MONITOR", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            sid_text = f"FPS: {fps:.0f} | ID: {session_manager.session_id or 'N/A'}"
            cv2.putText(frame, sid_text, (20, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (180, 180, 180), 1)

            # Raw Telemetry
            face_str = "Face: DETECTED" if face_detected else "Face: NOT DETECTED"
            face_col = (0, 255, 0) if face_detected else (0, 0, 255)
            cv2.putText(frame, face_str, (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.50, face_col, 1)

            if face_detected and eye_data:
                eye_str = f"Eye Ratio: {eye_data['average_ratio']:.2f} ({'CLOSED' if is_eyes_closed else 'OPEN'})"
                cv2.putText(frame, eye_str, (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 0), 1)

            gaze_dir = gaze_data["direction"] if gaze_data else "N/A"
            gaze_col = (0, 255, 0) if gaze_dir in ("SCREEN", "DOWN") else (0, 0, 255)
            cv2.putText(frame, f"Gaze: {gaze_dir}", (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.50, gaze_col, 1)

            p_score = cached_posture.get("posture_score", 1.0)
            p_col = (0, 255, 0) if not is_slouching else (0, 0, 255)
            p_status = "POOR" if is_slouching else "GOOD"
            cv2.putText(frame, f"Posture: {p_status} ({p_score:.2f})", (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.50, p_col, 1)

            obj_str = f"Phone: {'YES' if cached_phone_detected else 'NO'} | Book: {'YES' if cached_book_detected else 'NO'}"
            cv2.putText(frame, obj_str, (20, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (200, 200, 200), 1)

            # Separator Line
            cv2.line(frame, (20, 180), (470, 180), (70, 70, 70), 1)

            # Longitudinal Behavioral State + Confidence
            conf_pct = int(round(state_confidence * 100.0))
            state_text = f"STATE: {current_study_state.value.upper()} ({conf_pct}%)"
            state_color = (0, 255, 0) if current_study_state in (StudyState.FOCUSED, StudyState.READING) else (0, 0, 255)
            cv2.putText(frame, state_text, (20, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.75, state_color, 2)

            # Longitudinal Focus Ratio / Score
            session_sum = session_manager.summary()
            focus_pct = session_sum["focus_percentage"]
            focus_col = (0, 255, 0) if focus_pct >= 75 else ((0, 255, 255) if focus_pct >= 50 else (0, 0, 255))
            cv2.putText(frame, f"SESSION FOCUS: {focus_pct:.0f}%", (20, 245), cv2.FONT_HERSHEY_SIMPLEX, 0.85, focus_col, 2)

            # Focus Streak
            cur_streak = SessionMetrics.format_duration(session_sum["current_focus_streak"])
            best_streak = SessionMetrics.format_duration(session_sum["longest_focus_streak"])
            cv2.putText(frame, f"STREAK: {cur_streak} (BEST: {best_streak})", (20, 275), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 215, 0), 2)

            # Distraction Episodes & Average Recovery Time
            tot_dist = SessionMetrics.format_duration(sum(session_sum["distraction_episodes"]))
            avg_rec = SessionMetrics.format_duration(session_sum["average_recovery_time"])
            dist_str = f"DISTRACTIONS: {session_sum['distraction_count']} ({tot_dist}) | REC: {avg_rec}"
            cv2.putText(frame, dist_str, (20, 305), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (200, 200, 255), 1)

            # Breakdown Bar
            f_time = SessionMetrics.format_duration(session_sum["focused_time"])
            r_time = SessionMetrics.format_duration(session_sum["reading_time"])
            p_time = SessionMetrics.format_duration(session_sum["phone_time"])
            breakdown_str = f"Foc: {f_time} | Read: {r_time} | Phone: {p_time}"
            cv2.putText(frame, breakdown_str, (20, 335), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (170, 170, 170), 1)

            # Status saved tag
            cv2.putText(frame, "DB: ACTIVE (SQLite)", (20, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (100, 255, 100), 1)

            # Warning banner
            alert_manager.draw_visual_warning(frame)

            # --------------------------------
            # 10. Render Frame
            # --------------------------------
            cv2.imshow("Smart Study Monitor - Phase 8", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    except RuntimeError as error:
        print(f"[ERROR] {error}")
    except KeyboardInterrupt:
        print("\n[INFO] Application interrupted.")
    finally:
        # Finalize and persist session record
        finalized_session = session_manager.end_session()
        if finalized_session:
            print(f"\n[INFO] Study Session Saved to Database:")
            print(f"       Session ID:   {finalized_session.id}")
            print(f"       Duration:     {SessionMetrics.format_duration(finalized_session.duration)}")
            print(f"       Focus Score:  {finalized_session.focus_score:.1f}%")
            print(f"       Focused Time: {SessionMetrics.format_duration(finalized_session.focused_time)}")
            print(f"       Distractions: {finalized_session.distraction_count}")

        db_manager.close()
        camera.release()
        face_detector.close()
        pose_detector.close()
        alert_manager.close()


if __name__ == "__main__":
    main()
