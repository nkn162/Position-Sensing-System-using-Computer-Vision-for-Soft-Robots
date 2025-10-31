import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the images
image1 = cv2.imread('Trial_Image_1.jpg', cv2.IMREAD_GRAYSCALE)
image2 = cv2.imread('Trial_Image_2.jpg', cv2.IMREAD_GRAYSCALE)

# Apply Gaussian blur to reduce noise
blurred1 = cv2.GaussianBlur(image1, (5, 5), 0)
blurred2 = cv2.GaussianBlur(image2, (5, 5), 0)

# Apply Canny edge detection
edges1 = cv2.Canny(blurred1, 50, 150)
edges2 = cv2.Canny(blurred2, 50, 150)

# Perform small morphological closing operation to join fragmented edges
kernel = np.ones((3, 3), np.uint8)  # Small kernel to join fragments
closing1 = cv2.morphologyEx(edges1, cv2.MORPH_CLOSE, kernel)
closing2 = cv2.morphologyEx(edges2, cv2.MORPH_CLOSE, kernel)

# Compute gradient magnitude and angle
sobel_x1 = cv2.Sobel(closing1, cv2.CV_64F, 1, 0, ksize=3)
sobel_y1 = cv2.Sobel(closing1, cv2.CV_64F, 0, 1, ksize=3)
gradient_magnitude1 = cv2.magnitude(sobel_x1, sobel_y1)
gradient_angle1 = cv2.phase(sobel_x1, sobel_y1, angleInDegrees=True)

sobel_x2 = cv2.Sobel(closing2, cv2.CV_64F, 1, 0, ksize=3)
sobel_y2 = cv2.Sobel(closing2, cv2.CV_64F, 0, 1, ksize=3)
gradient_magnitude2 = cv2.magnitude(sobel_x2, sobel_y2)
gradient_angle2 = cv2.phase(sobel_x2, sobel_y2, angleInDegrees=True)

# Filter the edges to retain only horizontal lines (angle close to 0 or 180 degrees)
# We will use stricter thresholds (within 10 degrees of horizontal) to eliminate vertical lines
horizontal_mask1 = np.logical_or(
    (gradient_angle1 >= 170) & (gradient_angle1 <= 180), 
    (gradient_angle1 >= 0) & (gradient_angle1 <= 10)
)
horizontal_mask2 = np.logical_or(
    (gradient_angle2 >= 170) & (gradient_angle2 <= 180), 
    (gradient_angle2 >= 0) & (gradient_angle2 <= 10)
)

# Apply the mask to the gradient magnitude to keep only the horizontal edges
horizontal_edges1 = np.zeros_like(closing1)
horizontal_edges2 = np.zeros_like(closing2)
horizontal_edges1[horizontal_mask1] = closing1[horizontal_mask1]
horizontal_edges2[horizontal_mask2] = closing2[horizontal_mask2]

# Show the results
plt.subplot(2, 2, 1)
plt.imshow(edges1, cmap='gray')
plt.title('Canny Edges Image 1')

plt.subplot(2, 2, 2)
plt.imshow(closing1, cmap='gray')
plt.title('Post-Processed Edges Image 1')

plt.subplot(2, 2, 3)
plt.imshow(edges2, cmap='gray')
plt.title('Canny Edges Image 2')

plt.subplot(2, 2, 4)
plt.imshow(closing2, cmap='gray')
plt.title('Post-Processed Edges Image 2')

plt.show()

# Optionally, save the result
cv2.imwrite('output_image1.png', horizontal_edges1)
cv2.imwrite('output_image2.png', horizontal_edges2)
