from src.pose.posture_analyzer import PostureAnalyzer


def test_posture_analyzer_good_posture():
    analyzer = PostureAnalyzer()
    # Mock 33 landmarks: (x, y, z, visibility)
    landmarks = [(0, 0, 0.0, 1.0)] * 33

    # Head at (320, 150)
    landmarks[0] = (320, 150, 0.0, 1.0)
    # Left shoulder at (220, 300)
    landmarks[11] = (220, 300, 0.0, 1.0)
    # Right shoulder at (420, 300)
    landmarks[12] = (420, 300, 0.0, 1.0)
    # Midpoint of shoulders is (320, 300) -> perfectly aligned horizontally with head

    result = analyzer.analyze(landmarks)
    assert result["detected"] is True
    assert result["is_slouching"] is False
    assert result["posture_score"] >= 0.90
    assert result["shoulder_tilt"] == 0.0
    assert result["head_offset"] == 0.0


def test_posture_analyzer_tilted_shoulders():
    analyzer = PostureAnalyzer()
    landmarks = [(0, 0, 0.0, 1.0)] * 33

    # Head at (320, 150)
    landmarks[0] = (320, 150, 0.0, 1.0)
    # Left shoulder dropped at (220, 360) vs Right shoulder at (420, 280) -> dy = 80, width = 200 -> tilt = 0.40
    landmarks[11] = (220, 360, 0.0, 1.0)
    landmarks[12] = (420, 280, 0.0, 1.0)

    result = analyzer.analyze(landmarks)
    assert result["detected"] is True
    assert result["is_slouching"] is True
    assert result["shoulder_tilt"] > 0.15


def test_posture_analyzer_head_lateral_lean():
    analyzer = PostureAnalyzer()
    landmarks = [(0, 0, 0.0, 1.0)] * 33

    # Head shifted far right at (450, 150)
    landmarks[0] = (450, 150, 0.0, 1.0)
    # Shoulders at (220, 300) and (420, 300) -> midpoint is 320 -> offset is 130/200 = 0.65
    landmarks[11] = (220, 300, 0.0, 1.0)
    landmarks[12] = (420, 300, 0.0, 1.0)

    result = analyzer.analyze(landmarks)
    assert result["detected"] is True
    assert result["is_slouching"] is True
    assert result["head_offset"] > 0.25
