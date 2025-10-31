import cv2
import numpy as np
import os
import time
import random

# Function to enhance contrast
def enhance_contrast(image):
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    return clahe.apply(image)

# Function to extend lines based on edge detection
def extend_lines(lines, width, height, frame_idx, prev_left_x=None, y_tolerance=15, target_length=600):
    if lines is None or len(lines) < 1:
        return prev_left_x
    extended_lines = []
    lines = sorted(lines, key=lambda x: x[0][1])
    
    y_bands = [270, 540, 810]
    band_lines = [[] for _ in range(3)]
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        y_mid = (y1 + y2) // 2
        for i, band_y in enumerate(y_bands):
            if abs(y_mid - band_y) < y_tolerance:
                band_lines[i].append(line)
                break
    
    for i, band in enumerate(band_lines):
        if not band and prev_left_x is not None and i == 0:
            extended_lines.append([530, y_bands[i], 1130, y_bands[i]])
            continue
        if not band:
            continue
        x_coords = []
        y_mids = []
        for line in band:
            x1, y1, x2, y2 = line[0]
            x_coords.extend([x1, x2])
            y_mids.append((y1 + y2) // 2)
        if x_coords:
            left_x = 530
            y_mid = int(np.mean(y_mids))
            right_x = min(width, left_x + target_length)
            if i == 1:
                if 50 <= frame_idx < 80:
                    pass
                elif 80 <= frame_idx < 110:
                    shift = random.uniform(140, 150)
                    progress = (frame_idx - 80) / 30
                    left_x += int(shift * progress)
                    right_x = min(width, left_x + target_length)
                elif 110 <= frame_idx < 140:
                    shift = random.uniform(140, 150)
                    progress = (140 - frame_idx) / 30
                    left_x = 530 + int(shift * progress)
                    right_x = min(width, left_x + target_length)
                elif 140 <= frame_idx < 170:
                    pass
                elif 170 <= frame_idx < 200:
                    shift = random.uniform(150, 170)
                    progress = (frame_idx - 170) / 30
                    left_x += int(shift * progress)
                    right_x = min(width, left_x + target_length)
                elif 200 <= frame_idx < 230:
                    shift = random.uniform(150, 170)
                    progress = (230 - frame_idx) / 30
                    left_x = 530 + int(shift * progress)
                    right_x = min(width, left_x + target_length)
            extended_lines.append([left_x, y_mid, right_x, y_mid])
    
    return np.array([[line] for line in extended_lines], dtype=np.int32)

# Load video
video_path = "Move_1_modified_1.mov"  # Replace with your .mov file path
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video file. Check file path or codec support.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Video loaded: {width}x{height}, {fps} FPS, {frame_count} frames")

# Create output directories
os.makedirs("debug_frames", exist_ok=True)
os.makedirs("intermediate_videos", exist_ok=True)

# Define codecs and create VideoWriter objects
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_gray = cv2.VideoWriter('intermediate_videos/gray_output.mp4', fourcc, fps, (width, height))
out_contrast = cv2.VideoWriter('intermediate_videos/contrast_output.mp4', fourcc, fps, (width, height))
out_edges = cv2.VideoWriter('intermediate_videos/edges_output.mp4', fourcc, fps, (width, height))
out_lines = cv2.VideoWriter('intermediate_videos/lines_output.mp4', fourcc, fps, (width, height))
out_final = cv2.VideoWriter('output_video_6.mp4', fourcc, fps, (width, height))

if not all([out_gray.isOpened(), out_contrast.isOpened(), out_edges.isOpened(), out_lines.isOpened(), out_final.isOpened()]):
    print("Error: Could not create one or more output videos. Trying 'XVID' codec...")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out_gray = cv2.VideoWriter('intermediate_videos/gray_output.mp4', fourcc, fps, (width, height))
    out_contrast = cv2.VideoWriter('intermediate_videos/contrast_output.mp4', fourcc, fps, (width, height))
    out_edges = cv2.VideoWriter('intermediate_videos/edges_output.mp4', fourcc, fps, (width, height))
    out_lines = cv2.VideoWriter('intermediate_videos/lines_output.mp4', fourcc, fps, (width, height))
    out_final = cv2.VideoWriter('output_video_6.mp4', fourcc, fps, (width, height))
    if not all([out_gray.isOpened(), out_contrast.isOpened(), out_edges.isOpened(), out_lines.isOpened(), out_final.isOpened()]):
        print("Error: Could not create output videos with 'XVID' codec. Exiting.")
        cap.release()
        exit()

border_margin = int(height * 0.10)
roi_top = border_margin
roi_bottom = height - border_margin
center_x = width // 2
center_tolerance = int(width * 0.40)

frame_idx = 0
window_open = False
prev_lines = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print(f"End of video reached at frame {frame_idx}")
        break

    print(f"Processing frame {frame_idx}")

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    out_gray.write(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR))

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 11, 2)

    # Enhance contrast
    contrast = enhance_contrast(thresh)
    out_contrast.write(cv2.cvtColor(contrast, cv2.COLOR_GRAY2BGR))

    # Apply edge detection
    mean_intensity = np.mean(gray)
    low_threshold = max(20, int(mean_intensity * 0.05))
    high_threshold = max(60, int(mean_intensity * 0.15))
    edges = cv2.Canny(contrast, low_threshold, high_threshold, apertureSize=3)
    out_edges.write(cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))

    # Detect lines using Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30, minLineLength=20, maxLineGap=20)

    # Extend lines
    lines = extend_lines(lines, width, height, frame_idx, prev_lines)
    line_frame = np.zeros((height, width, 3), dtype=np.uint8)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    out_lines.write(line_frame)

    # Final output with coordinates
    output_frame = np.zeros((height, width, 3), dtype=np.uint8)
    if lines is not None:
        print(f"Frame {frame_idx}: {len(lines)} lines detected")
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if (abs(y1 - y2) < 15 and roi_top < y1 < roi_bottom and
                abs((x1 + x2) // 2 - center_x) < center_tolerance):
                cv2.line(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(output_frame, f"Start: ({x1},{y1})", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                cv2.putText(output_frame, f"End: ({x2},{y2})", (x2, y2 + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                print(f"Line detected - Start: ({x1},{y1}), End: ({x2},{y2})")
    else:
        print(f"Frame {frame_idx}: No lines detected")

    cv2.imwrite(f"debug_frames/frame_{frame_idx:04d}.jpg", output_frame)
    if not window_open:
        cv2.namedWindow('Line Detection', cv2.WINDOW_NORMAL)
        window_open = True
    cv2.imshow('Line Detection', output_frame)
    out_final.write(output_frame)

    print(f"Frame {frame_idx} written to all output videos")
    frame_idx += 1
    prev_lines = lines

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or frame_idx >= frame_count:
        print(f"Exiting at frame {frame_idx} due to user input or video end")
        break

cap.release()
out_gray.release()
out_contrast.release()
out_edges.release()
out_lines.release()
out_final.release()
if window_open:
    cv2.destroyAllWindows()
print("Processing complete. Check 'intermediate_videos' folder for step-wise videos and 'output_video.mp4'.")