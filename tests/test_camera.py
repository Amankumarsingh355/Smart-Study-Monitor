import cv2


def test_camera_available():

    camera = cv2.VideoCapture(0)

    assert camera.isOpened(), "Camera could not be opened."

    camera.release()
