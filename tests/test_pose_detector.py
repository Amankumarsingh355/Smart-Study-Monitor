import numpy as np
from src.pose.pose_detector import PoseDetector


def test_pose_detector_initialization():
    detector = PoseDetector()
    assert detector.min_detection_confidence == 0.5
    detector.close()


def test_pose_detector_dummy_frame():
    detector = PoseDetector()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    landmarks = detector.process(dummy_frame)
    assert landmarks is None
    detector.close()
