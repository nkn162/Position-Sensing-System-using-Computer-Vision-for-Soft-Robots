import cv2
import numpy as np
import os

# Function to enhance contrast
def enhance_contrast(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)

# Function to merge line segments
def merge_lines(lines, y_threshold=10, x_gap_threshold=20):
    if lines is None:
        return None
    merged_lines = []
    lines = sorted(lines, key=lambda x: x[0][1])  # Sort by y-coordinate
    i = 0
    while i < len(lines):
        x1, y1, x2, y2 = lines[i][0]
        current_line = [x1, y1, x2, y2]
        j = i + 1
        while j < len(lines):
            nx1, ny1, nx2, ny2 = lines[j][0]
            if (abs(y1 - ny1) < y_threshold and abs(y2 - ny2) < y_threshold and
                min(abs(x2 - nx1), abs(x1 - nx2)) < x_gap_threshold):
                # Merge lines
                current_line[0] = min(x1, nx1, x2, nx2)
                current_line[2] = max(x1, nx1, x2, nx2)
                current_line[1] = (y1 + ny1) // 2
                current_line[3] = (y2 + ny2) // 2
                i = j
            else:
                break
            j += 1
        merged_lines.append(current_line)
        i += 1
    return np.array([[line] for line in merged_lines], dtype=np.int32)

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
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output_video_2.mp4', fourcc, fps, (width, height))
if not out.isOpened():
    print("Error: Could not create output video. Check codec compatibility.")
    exit()

# Define ROI to exclude borders (e.g., 5% from top and bottom)
border_margin = int(height * 0.05)
roi_top = border_margin
roi_bottom = height - border_margin

frame_idx = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("End of video or error reading frame.")
        break

    print(f"Processing frame {frame_idx}")

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply intensity thresholding to focus on dark lines
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

    # Enhance contrast
    contrast = enhance_contrast(thresh)

    # Apply edge detection
    edges = cv2.Canny(contrast, 50, 150, apertureSize=3)

    # Apply ROI mask to exclude borders
    mask = np.zeros_like(edges)
    mask[roi_top:roi_bottom, :] = edges[roi_top:roi_bottom, :]
    edges = mask

    # Detect lines using Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60, minLineLength=50, maxLineGap=30)

    # Merge line segments
    lines = merge_lines(lines)

    # Create black background for output
    output_frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Process detected lines and draw them
    if lines is not None:
        print(f"Frame {frame_idx}: {len(lines)} lines detected")
        # Limit to 3 lines (sort by y-coordinate and take top 3)
        lines = sorted(lines, key=lambda x: x[0][1])[:3]
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Filter for near-horizontal lines
            if abs(y1 - y2) < 15 and roi_top < y1 < roi_bottom and roi_top < y2 < roi_bottom:
                cv2.line(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # Optional: Draw coordinates
                cv2.putText(output_frame, f"Start: ({x1},{y1})", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                cv2.putText(output_frame, f"End: ({x2},{y2})", (x2, y2 + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                print(f"Line detected - Start: ({x1},{y1}), End: ({x2},{y2})")
    else:
        print(f"Frame {frame_idx}: No lines detected")

    # Save debug frame
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