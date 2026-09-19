from src.face.eye_analyzer import EyeAnalyzer


def test_distance_calculation():
    analyzer = EyeAnalyzer()
    point_a = (0, 0)
    point_b = (3, 4)
    dist = analyzer._distance(point_a, point_b)
    assert dist == 5.0


def test_eye_ratio_open_state():
    analyzer = EyeAnalyzer()

    # Create dummy landmarks (468 points initialized to (0, 0))
    landmarks = [(0, 0)] * 468

    # Left eye: corners (10, 50) and (40, 50) -> width = 30
    # Top (25, 45) and bottom (25, 55) -> height = 10
    # Ratio = 10 / 30 = 0.333
    landmarks[33] = (10, 50)
    landmarks[133] = (40, 50)
    landmarks[159] = (25, 45)
    landmarks[145] = (25, 55)

    ratio = analyzer.calculate_eye_ratio(landmarks, EyeAnalyzer.LEFT_EYE)
    assert round(ratio, 3) == 0.333

    state = analyzer.get_eye_state(ratio, threshold=0.20)
    assert state == "OPEN"


def test_eye_ratio_closed_state():
    analyzer = EyeAnalyzer()

    landmarks = [(0, 0)] * 468

    # Left eye: corners (10, 50) and (40, 50) -> width = 30
    # Top (25, 50) and bottom (25, 52) -> height = 2
    # Ratio = 2 / 30 = 0.0667
    landmarks[33] = (10, 50)
    landmarks[133] = (40, 50)
    landmarks[159] = (25, 50)
    landmarks[145] = (25, 52)

    ratio = analyzer.calculate_eye_ratio(landmarks, EyeAnalyzer.LEFT_EYE)
    assert round(ratio, 4) == 0.0667

    state = analyzer.get_eye_state(ratio, threshold=0.20)
    assert state == "CLOSED"


def test_eye_ratio_zero_horizontal_distance():
    analyzer = EyeAnalyzer()
    landmarks = [(0, 0)] * 468
    # Left and right corner at same point
    landmarks[33] = (10, 50)
    landmarks[133] = (10, 50)
    landmarks[159] = (10, 45)
    landmarks[145] = (10, 55)

    ratio = analyzer.calculate_eye_ratio(landmarks, EyeAnalyzer.LEFT_EYE)
    assert ratio == 0.0
    assert analyzer.get_eye_state(ratio) == "CLOSED"


def test_analyze_both_eyes():
    analyzer = EyeAnalyzer()
    landmarks = [(0, 0)] * 468

    # Left eye
    landmarks[33] = (10, 50)
    landmarks[133] = (40, 50)
    landmarks[159] = (25, 45)
    landmarks[145] = (25, 55)

    # Right eye
    landmarks[362] = (110, 50)
    landmarks[263] = (140, 50)
    landmarks[386] = (125, 45)
    landmarks[374] = (125, 55)

    results = analyzer.analyze(landmarks)

    assert "left_ratio" in results
    assert "right_ratio" in results
    assert "average_ratio" in results
    assert round(results["average_ratio"], 3) == 0.333
