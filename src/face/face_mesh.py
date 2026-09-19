import os
import urllib.request
import cv2
import mediapipe as mp


class _FaceLandmarksContainer:
    """Wrapper providing .landmark attribute matching mp.solutions schema."""
    def __init__(self, landmarks):
        self.landmark = landmarks


class _FaceMeshResults:
    """Wrapper providing .multi_face_landmarks matching mp.solutions schema."""
    def __init__(self, face_landmarks_list):
        if face_landmarks_list:
            self.multi_face_landmarks = [
                _FaceLandmarksContainer(lm) for lm in face_landmarks_list
            ]
        else:
            self.multi_face_landmarks = None


class FaceMeshDetector:
    """
    Handles facial landmark detection.

    The rest of the application communicates
    with this class instead of directly using MediaPipe.

    Supports both legacy mp.solutions (MediaPipe < 0.10.30)
    and modern mp.tasks.vision.FaceLandmarker (MediaPipe 0.10.30+ / Python 3.13).
    """

    def __init__(
        self,
        max_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ):

        self.max_faces = max_faces
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
            self.mode = "solutions"
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=self.max_faces,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
        else:
            self.mode = "tasks"
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision

            model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "models",
                "face_landmarker.task"
            )
            if not os.path.exists(model_path):
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
                urllib.request.urlretrieve(url, model_path)

            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.IMAGE,
                num_faces=self.max_faces,
                min_face_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )
            self.face_mesh = vision.FaceLandmarker.create_from_options(options)

    def process(self, frame):
        """
        Process an OpenCV BGR frame.

        Returns:
            results: Results object with multi_face_landmarks attribute.
        """

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        if self.mode == "solutions":
            results = self.face_mesh.process(rgb_frame)
            return results
        else:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = self.face_mesh.detect(mp_image)
            return _FaceMeshResults(detection_result.face_landmarks)

    def close(self):
        """Release MediaPipe resources."""

        self.face_mesh.close()
