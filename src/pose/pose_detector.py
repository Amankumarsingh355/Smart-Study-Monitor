import os
import urllib.request
import cv2
import mediapipe as mp
from typing import List, Tuple, Optional


class PoseDetector:
    """
    Handles body pose estimation using MediaPipe Pose.
    Decoupled from application logic; only provides 3D landmark coordinates.
    """

    def __init__(self, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "models",
            "pose_landmarker_lite.task"
        )
        if not os.path.exists(model_path):
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
            urllib.request.urlretrieve(url, model_path)

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def process(self, frame) -> Optional[List[Tuple[int, int, float, float]]]:
        """
        Process an OpenCV BGR frame.

        Returns:
            List of 33 landmarks as (x_pixel, y_pixel, z_norm, visibility),
            or None if no pose is detected.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = self.landmarker.detect(mp_image)

        if not result.pose_landmarks or len(result.pose_landmarks) == 0:
            return None

        height, width, _ = frame.shape
        landmarks = []
        for lm in result.pose_landmarks[0]:
            x_px = int(lm.x * width)
            y_px = int(lm.y * height)
            landmarks.append((x_px, y_px, lm.z, getattr(lm, "visibility", 1.0)))

        return landmarks

    def close(self):
        """Release landmarker resources."""
        self.landmarker.close()
