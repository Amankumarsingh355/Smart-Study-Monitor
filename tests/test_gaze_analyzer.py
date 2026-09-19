from src.gaze.gaze_analyzer import GazeAnalyzer


def test_gaze_analyzer_screen_center():
    analyzer = GazeAnalyzer()
    landmarks = [(0, 0)] * 478

    # Left temple at (150, 200), Right temple at (350, 200) -> temple mid is 250
    # Forehead at (250, 100), Chin at (250, 300) -> face mid_y is 200
    # Nose at (250, 200) -> perfectly centered
    landmarks[GazeAnalyzer.LEFT_TEMPLE] = (150, 200)
    landmarks[GazeAnalyzer.RIGHT_TEMPLE] = (350, 200)
    landmarks[GazeAnalyzer.FOREHEAD] = (250, 100)
    landmarks[GazeAnalyzer.CHIN] = (250, 300)
    landmarks[GazeAnalyzer.NOSE_TIP] = (250, 200)

    result = analyzer.analyze(landmarks)
    assert result["direction"] == "SCREEN"
    assert not result["is_looking_away"]
    assert not result["is_looking_down"]


def test_gaze_analyzer_looking_left():
    analyzer = GazeAnalyzer()
    landmarks = [(0, 0)] * 478

    landmarks[GazeAnalyzer.LEFT_TEMPLE] = (150, 200)
    landmarks[GazeAnalyzer.RIGHT_TEMPLE] = (350, 200)
    landmarks[GazeAnalyzer.FOREHEAD] = (250, 100)
    landmarks[GazeAnalyzer.CHIN] = (250, 300)
    # Nose turned far left to x = 180 (temple mid = 250, width = 200 -> yaw = (180 - 250)/200 = -0.35)
    landmarks[GazeAnalyzer.NOSE_TIP] = (180, 200)

    result = analyzer.analyze(landmarks)
    assert result["direction"] == "LEFT"
    assert result["is_looking_away"] is True


def test_gaze_analyzer_looking_down():
    analyzer = GazeAnalyzer()
    landmarks = [(0, 0)] * 478

    landmarks[GazeAnalyzer.LEFT_TEMPLE] = (150, 200)
    landmarks[GazeAnalyzer.RIGHT_TEMPLE] = (350, 200)
    landmarks[GazeAnalyzer.FOREHEAD] = (250, 100)
    landmarks[GazeAnalyzer.CHIN] = (250, 300)
    # Nose pitched down to y = 250 (mid_y = 200, height = 200 -> pitch = (250 - 200)/200 = 0.25)
    landmarks[GazeAnalyzer.NOSE_TIP] = (250, 250)

    result = analyzer.analyze(landmarks)
    assert result["direction"] == "DOWN"
    assert result["is_looking_down"] is True
    assert result["is_looking_away"] is False
