import numpy as np
from src.detection.object_detector import ObjectDetector


def test_object_detector_initialization():
    detector = ObjectDetector(model_name="yolov8n.pt", target_classes=["cell phone"])
    assert detector.model_name == "yolov8n.pt"
    assert "cell phone" in detector.target_classes


def test_object_detector_dummy_frame():
    detector = ObjectDetector(model_name="yolov8n.pt", target_classes=["cell phone"])
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    is_phone, boxes = detector.is_phone_visible(dummy_frame)
    assert isinstance(is_phone, bool)
    assert not is_phone
    assert len(boxes) == 0
