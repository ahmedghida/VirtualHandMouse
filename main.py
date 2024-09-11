import cv2
import utils
import mediapipe as mp

def is_mouse_moving(land_marks, thumb2ind):
    """
    Determines if the mouse should move based on hand posture.
    
    Args:
        land_marks: List of hand landmarks.
        thumb2ind: Distance between thumb and index finger.
        
    Returns:
        bool: True if the mouse should move, False otherwise.
    """
    index_finger_angle = utils.calculate_angle(land_marks[8], land_marks[6], land_marks[5])
    thumb_angle = utils.calculate_angle(land_marks[12], land_marks[10], land_marks[9])
    
    return (index_finger_angle > 90 and thumb2ind < 50 and thumb_angle > 50)

def is_left_click(land_marks, thumb2ind):
    """
    Determines if a left-click should be performed based on hand posture.
    
    Args:
        land_marks: List of hand landmarks.
        thumb2ind: Distance between thumb and index finger.
        
    Returns:
        bool: True if a left-click should be performed, False otherwise.
    """
    index_finger_angle = utils.calculate_angle(land_marks[8], land_marks[6], land_marks[5])
    thumb_angle = utils.calculate_angle(land_marks[12], land_marks[10], land_marks[9])
    
    return (thumb2ind > 50 and index_finger_angle < 50 and thumb_angle > 50)

def is_right_click(land_marks, thumb2ind):
    """
    Determines if a right-click should be performed based on hand posture.
    
    Args:
        land_marks: List of hand landmarks.
        thumb2ind: Distance between thumb and index finger.
        
    Returns:
        bool: True if a right-click should be performed, False otherwise.
    """
    index_finger_angle = utils.calculate_angle(land_marks[8], land_marks[6], land_marks[5])
    thumb_angle = utils.calculate_angle(land_marks[12], land_marks[10], land_marks[9])
    
    return (thumb2ind > 50 and index_finger_angle > 50 and thumb_angle < 50)

def is_double_click(land_marks, thumb2ind):
    """
    Determines if a double-click should be performed based on hand posture.
    
    Args:
        land_marks: List of hand landmarks.
        thumb2ind: Distance between thumb and index finger.
        
    Returns:
        bool: True if a double-click should be performed, False otherwise.
    """
    index_finger_angle = utils.calculate_angle(land_marks[8], land_marks[6], land_marks[5])
    thumb_angle = utils.calculate_angle(land_marks[12], land_marks[10], land_marks[9])
    
    return (thumb2ind > 50 and index_finger_angle < 50 and thumb_angle < 50)

def main():
    # Initialize the MouseController from utils
    mouse = utils.MouseController()

    # Initialize MediaPipe Hands
    model = mp.solutions.hands.Hands(
        static_image_mode=False, 
        max_num_hands=1, 
        min_detection_confidence=0.5
    )

    # Initialize the drawer to visualize hand landmarks
    drawer = mp.solutions.drawing_utils

    # Initialize the camera (0 for the default camera)
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video camera.")
        return

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        (h, w) = frame.shape[:2]

        # Define the center of the image (around which rotation happens)
        center = (w // 2, h // 2)

        # Define the rotation angle (e.g., 45 degrees) and scaling factor (1 means no scaling)
        angle = 90
        scale = 1.0

        # Get the rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)

        # Perform the rotation
        frame = cv2.warpAffine(frame, rotation_matrix, (w, h))

        frame=frame[:,140:-140]

        frame=cv2.resize(frame,(640,480))

        frame_height, frame_width, _ = frame.shape
        
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Process the frame to find hand landmarks
        results = model.process(frame)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            drawer.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
            
            # Convert hand landmarks to a format suitable for calculations
            hand_landmarks = utils.format_landmarks(hand_landmarks)
            
            # Calculate distance between thumb and index finger
            thumb2ind_distance = utils.get_distance(hand_landmarks[5], hand_landmarks[4])

            # Perform mouse actions based on hand gestures
            if is_mouse_moving(hand_landmarks, thumb2ind_distance):

                index_finger_x, index_finger_y = int(hand_landmarks[8][0]*frame_width), int(hand_landmarks[8][1]*frame_height)
                mouse.move_mouse(index_finger_x, index_finger_y, frame_width, frame_height)

            elif is_left_click(hand_landmarks, thumb2ind_distance):
                cv2.putText(frame,'left_click',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),3)
                mouse.left_click()

            elif is_right_click(hand_landmarks, thumb2ind_distance):
                cv2.putText(frame,'right_click',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),3)
                mouse.right_click()

            elif is_double_click(hand_landmarks, thumb2ind_distance):
                cv2.putText(frame,'double_click',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),3)
                mouse.double_click()

        # Display the resulting frame
        cv2.imshow('Camera Feed', frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
