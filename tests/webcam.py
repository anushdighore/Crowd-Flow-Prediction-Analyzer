import cv2

# Use the /video endpoint from the IP Webcam app
IP_WEB_CAM_URL = "http://192.168.137.154:8080/video"

# Open the video stream
cap = cv2.VideoCapture(IP_WEB_CAM_URL)

if not cap.isOpened():
    print("Error: Could not open video stream. Check the URL and network connection.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Display the frame
    cv2.imshow("IP Webcam Stream", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()