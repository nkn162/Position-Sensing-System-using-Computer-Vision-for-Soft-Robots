import cv2
import numpy as np
import matplotlib.pyplot as plt

def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img_blur = cv2.GaussianBlur(img, (5, 5), 0)
    return img_blur

def detect_edges(image):
    # Adjust Canny thresholds for more continuous edges
    edges = cv2.Canny(image, 30, 250, apertureSize=3)
    return edges

def filter_horizontal_lines(edges):
    # Use Hough Line Transform to detect lines with adjusted parameters
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=30, minLineLength=120, maxLineGap=5)
    
    filtered_lines = np.zeros_like(edges)
    if lines is not None:
        # List to store lines with their coordinates
        unique_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            if -10 <= angle <= 10:  # Keep only near-horizontal lines
                # Avoid duplicate lines by checking for proximity
                add_line = True
                for existing_line in unique_lines:
                    ex_x1, ex_y1, ex_x2, ex_y2 = existing_line
                    if abs(ex_y1 - y1) < 5:  # Lines are considered duplicates if their y-coordinates are close
                        add_line = False
                        break
                if add_line:
                    unique_lines.append((x1, y1, x2, y2))
                    cv2.line(filtered_lines, (x1, y1), (x2, y2), 255, 1)  # Thin lines
    return filtered_lines

def post_process(image):
    kernel = np.ones((5, 5), np.uint8)  # Use smaller kernel for thinner lines
    dilated = cv2.dilate(image, kernel, iterations=3)
    thinned = cv2.erode(dilated, kernel, iterations=2)
    
    # Apply closing to help fill in gaps and connect fragmented edges
    kernel_close = np.ones((9, 9), np.uint8)
    closed = cv2.morphologyEx(thinned, cv2.MORPH_CLOSE, kernel_close)
    return closed

def process_image(image_path, output_path):
    img_blur = preprocess_image(image_path)
    edges = detect_edges(img_blur)
    horizontal_lines = filter_horizontal_lines(edges)
    final_output = post_process(horizontal_lines)
    
    # Save the output image
    cv2.imwrite(output_path, final_output)
    return final_output

# Process both images and save the output
image_paths = ["Trial_Image_1.jpg", "Trial_Image_2.jpg"]
output_paths = ["Processed_Image_1.jpg", "Processed_Image_2.jpg"]

# Pass the corresponding output path along with the image path
outputs = [process_image(img, output) for img, output in zip(image_paths, output_paths)]

# Display results
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
for ax, output, title in zip(axes, outputs, ["Image 1", "Image 2"]):
    ax.imshow(output, cmap='gray')
    ax.set_title(title)
    ax.axis("off")
plt.show()
