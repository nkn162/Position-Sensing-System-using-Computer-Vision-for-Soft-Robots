import cv2
import numpy as np
import os

# Function to enhance contrast
def enhance_contrast(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)

# Load video
video_path = "Move_1_modified_1.mov"  # Replace with your .mov file path
cap = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not cap.isOpened():
    print("Error: Could not open video file. Check file path or codec support.")
    exit()

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Video loaded: {width}x{height}, {fps} FPS, {frame_count} frames")

# Create output directory for debug frames
os.makedirs("debug_frames", exist_ok=True)

# Define codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Try 'XVID' or 'MJPG' if mp4v fails
out = cv2.VideoWriter('output_video.mp4', fourcc, fps, (width, height))
if not out.isOpened():
    print("Error: Could not create output video. Check codec compatibility.")
    exit()

frame_idx = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("End of video or error reading frame.")
        break

    print(f"Processing frame {frame_idx}")

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Enhance contrast
    contrast = enhance_contrast(gray)

    # Apply edge detection
    edges = cv2.Canny(contrast, 50, 150, apertureSize=3)

    # Detect lines using Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=30, maxLineGap=10)

    # Create a copy of the original frame for drawing
    output_frame = frame.copy()

    # Process detected lines and draw them
    if lines is not None:
        print(f"Frame {frame_idx}: {len(lines)} lines detected")
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Filter for near-horizontal lines
            if abs(y1 - y2) < 15:  # Relaxed threshold for horizontal lines
                cv2.line(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(output_frame, f"Start: ({x1},{y1})", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                cv2.putText(output_frame, f"End: ({x2},{y2})", (x2, y2 + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                print(f"Line detected - Start: ({x1},{y1}), End: ({x2},{y2})")
    else:
        print(f"Frame {frame_idx}: No lines detected")

    # Save debug frame as image
    cv2.imwrite(f"debug_frames/frame_{frame_idx:04d}.jpg", output_frame)

    # Display the frame
    cv2.imshow('Line Detection', output_frame)

    # Write to output video
    out.write(output_frame)

    frame_idx += 1

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()
print("Processing complete. Check 'debug_frames' folder for saved frames.")