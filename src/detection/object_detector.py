import os
from typing import List, Dict, Any, Tuple


class ObjectDetector:
    """
    Handles object detection using YOLOv8 nano.
    
    Adheres to separation of concerns:
    Only answers 'What objects are visible?' and does not handle events or alerts.
    """

    def __init__(self, model_name: str = "yolov8n.pt", target_classes: List[str] = None):
        self.model_name = model_name
        self.target_classes = target_classes or ["cell phone", "book"]
        self._model = None

    def _load_model(self):
        if self._model is None:
            from ultralytics import YOLO
            models_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "models"
            )
            os.makedirs(models_dir, exist_ok=True)
            model_path = os.path.join(models_dir, self.model_name)

            self._model = YOLO(model_path if os.path.exists(model_path) else self.model_name)

    def detect_objects(
        self,
        frame,
        confidence_threshold: float = 0.40
    ) -> List[Dict[str, Any]]:
        """
        Run object detection on an OpenCV BGR frame.

        Returns:
            List of detected objects:
            [
                {
                    "class_name": str,
                    "confidence": float,
                    "box": Tuple[int, int, int, int]  # (x1, y1, x2, y2)
                }
            ]
        """
        self._load_model()

        results = self._model.predict(
            source=frame,
            conf=confidence_threshold,
            verbose=False
        )

        detections = []

        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes

            for box in boxes:
                cls_id = int(box.cls[0].item())
                class_name = result.names.get(cls_id, "unknown")
                conf = float(box.conf[0].item())

                if class_name in self.target_classes:
                    xyxy = box.xyxy[0].tolist()
                    x1, y1, x2, y2 = map(int, xyxy)
                    detections.append({
                        "class_name": class_name,
                        "confidence": conf,
                        "box": (x1, y1, x2, y2)
                    })

        return detections

    def is_phone_visible(
        self,
        frame,
        confidence_threshold: float = 0.40
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Convenience method to check if a phone is currently visible in the frame.
        """
        detections = self.detect_objects(frame, confidence_threshold)
        phone_detections = [d for d in detections if d["class_name"] == "cell phone"]
        return len(phone_detections) > 0, phone_detections

    def is_book_visible(
        self,
        frame,
        confidence_threshold: float = 0.35
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Convenience method to check if a book is currently visible in the frame.
        """
        detections = self.detect_objects(frame, confidence_threshold)
        book_detections = [d for d in detections if d["class_name"] == "book"]
        return len(book_detections) > 0, book_detections
