import numpy as np
from screeninfo import get_monitors
from pynput.mouse import Button, Controller

def format_landmarks(hand_landmarks):
    """
    Convert MediaPipe hand landmarks to a NumPy array of (x, y) coordinates.

    Args:
        hand_landmarks: MediaPipe hand landmarks object.

    Returns:
        np.ndarray: Array of (x, y) coordinates for each landmark.
    """
    if not hand_landmarks or not hand_landmarks.landmark:
        raise ValueError("Invalid hand landmarks provided.")
    
    return np.array([(cord.x, cord.y) for cord in hand_landmarks.landmark])

def calculate_angle(A, B, C):
    """
    Calculate the angle between three points.

    Args:
        A, B, C: Tuples representing (x, y) coordinates of the points.

    Returns:
        float: The angle in degrees between the points A, B, and C.
    """
    x1, y1 = A
    x2, y2 = B
    x3, y3 = C
    
    angle1 = np.arctan2(y1 - y2, x1 - x2)
    angle2 = np.arctan2(y3 - y2, x3 - x2)
    
    angle = np.degrees(angle1 - angle2)
    
    return angle + 360 if angle < 0 else angle

def get_distance(landmark1, landmark2):
    """
    Compute the distance between two landmarks.

    Args:
        landmark1, landmark2: Tuples representing (x, y) coordinates of the landmarks.

    Returns:
        float: The normalized distance between the two landmarks.
    """
    x1, y1 = landmark1
    x2, y2 = landmark2
    
    distance = np.hypot(x2 - x1, y2 - y1)
    return np.interp(distance, [0, 1], [0, 1000])

class MouseController:
    def __init__(self):
        """
        Initialize the MouseController with screen dimensions and pynput mouse controller.
        """
        self.mouse = Controller()
        self.monitor = get_monitors()[0]
        self.screen_width = self.monitor.width
        self.screen_height = self.monitor.height


    def move_mouse(self, x, y, frame_width, frame_height, sensitivity=1.0):
        """
        Move the mouse based on normalized hand coordinates from the video frame
        to the full desktop resolution.

        Args:
            x, y: Hand landmark coordinates in the video frame (normalized to [0, 1]).
            frame_width: Width of the video frame.
            frame_height: Height of the video frame.
            sensitivity: Adjusts the speed of mouse movement (1.0 = normal).
        """

        # Map the normalized (x, y) hand coordinates to desktop resolution
        x_pos = int(np.interp(x, [20, frame_width-20], [0, self.screen_width]) * sensitivity)
        y_pos = int(np.interp(y, [20, frame_height-20], [0, self.screen_height]) * (sensitivity+.2))

        # Ensure the mouse doesn't go out of screen bounds
        x_pos = np.clip(x_pos, 0, self.screen_width-20)
        y_pos = np.clip(y_pos, 0, self.screen_height-20)

        # Move the mouse to the new position
        self.mouse.position = (x_pos, y_pos)


    def left_click(self):
        """
        Perform a left-click at the current mouse position.
        """
        self.mouse.press(Button.left)
        self.mouse.release(Button.left)

    def right_click(self):
        """
        Perform a right-click at the current mouse position.
        """
        self.mouse.click(Button.right, 1)

    def double_click(self):
        """
        Perform a double-click with the left mouse button.
        """
        self.mouse.click(Button.left, 2)
