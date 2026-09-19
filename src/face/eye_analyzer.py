import math


class EyeAnalyzer:
    """
    Extracts eye-related measurements from facial landmarks.
    """

    # MediaPipe landmark indices used for eye geometry.
    #
    # These indices represent approximate eyelid/corner points.
    LEFT_EYE = {
        "left_corner": 33,
        "right_corner": 133,
        "top": 159,
        "bottom": 145
    }

    RIGHT_EYE = {
        "left_corner": 362,
        "right_corner": 263,
        "top": 386,
        "bottom": 374
    }

    @staticmethod
    def _distance(point_a, point_b):
        """Calculate Euclidean distance between two points."""

        dx = point_a[0] - point_b[0]
        dy = point_a[1] - point_b[1]

        return math.sqrt(
            dx * dx + dy * dy
        )

    def calculate_eye_ratio(
        self,
        landmarks,
        eye
    ):
        """
        Calculate a normalized eye-opening ratio.

        landmarks:
            List of facial landmarks.

        eye:
            Dictionary containing eye landmark indices.
        """

        left_corner = landmarks[
            eye["left_corner"]
        ]

        right_corner = landmarks[
            eye["right_corner"]
        ]

        top = landmarks[
            eye["top"]
        ]

        bottom = landmarks[
            eye["bottom"]
        ]

        horizontal_distance = self._distance(
            left_corner,
            right_corner
        )

        vertical_distance = self._distance(
            top,
            bottom
        )

        if horizontal_distance == 0:
            return 0.0

        ratio = vertical_distance / horizontal_distance

        return ratio

    def analyze(self, landmarks):
        """
        Analyze both eyes.

        Returns:
            Dictionary containing left eye,
            right eye and average ratio.
        """

        left_ratio = self.calculate_eye_ratio(
            landmarks,
            self.LEFT_EYE
        )

        right_ratio = self.calculate_eye_ratio(
            landmarks,
            self.RIGHT_EYE
        )

        average_ratio = (
            left_ratio + right_ratio
        ) / 2

        return {
            "left_ratio": left_ratio,
            "right_ratio": right_ratio,
            "average_ratio": average_ratio
        }

    def get_eye_state(
        self,
        eye_ratio,
        threshold=0.20
    ):
        """
        Classify eye state using a configurable threshold.

        NOTE:
        This threshold is only an initial heuristic.
        It must be calibrated for the actual camera/user.
        """

        if eye_ratio < threshold:
            return "CLOSED"

        return "OPEN"
