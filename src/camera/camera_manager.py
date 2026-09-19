import cv2
import time


class CameraManager:
    """
    Handles webcam initialization, frame capture,
    FPS calculation, and camera shutdown.
    """

    def __init__(self, camera_index=0, width=1280, height=720):
        self.camera_index = camera_index
        self.width = width
        self.height = height

        self.cap = None

        # FPS variables
        self.previous_time = time.time()
        self.fps = 0.0

    def start(self):
        """Initialize the webcam."""

        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Unable to open camera with index {self.camera_index}"
            )

        # Request desired resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        print("[INFO] Camera started successfully.")

    def read_frame(self):
        """
        Capture one frame from the webcam.

        Returns:
            frame: OpenCV BGR image
        """

        if self.cap is None:
            raise RuntimeError("Camera has not been started.")

        success, frame = self.cap.read()

        if not success:
            raise RuntimeError("Failed to read frame from camera.")

        self._calculate_fps()

        return frame

    def _calculate_fps(self):
        """Calculate current FPS."""

        current_time = time.time()

        time_difference = current_time - self.previous_time

        if time_difference > 0:
            self.fps = 1 / time_difference

        self.previous_time = current_time

    def get_fps(self):
        """Return current FPS."""

        return self.fps

    def release(self):
        """Release webcam resources."""

        if self.cap is not None:
            self.cap.release()

        cv2.destroyAllWindows()

        print("[INFO] Camera released.")
