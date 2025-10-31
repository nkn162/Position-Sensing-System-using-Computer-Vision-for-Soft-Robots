import cv2
import numpy as np
import matplotlib.pyplot as plt

print("Script is running...")

frame1 = cv2.imread('Trial_Image_1.jpg', cv2.IMREAD_GRAYSCALE)
frame2 = cv2.imread('Trial_Image_2.jpg', cv2.IMREAD_GRAYSCALE)

if frame1 is None or frame2 is None:
    print("Error: One or both images not found!")
    exit()
print("Images loaded successfully.")

# Gaussian filter
frame1_blurred = cv2.GaussianBlur(frame1, (5, 5), 0)
frame2_blurred = cv2.GaussianBlur(frame2, (5, 5), 0)

# # Compute gradients using Sobel operator
# grad_x1 = cv2.Sobel(frame1_blurred, cv2.CV_64F, 1, 0, ksize=3)  
# grad_y1 = cv2.Sobel(frame1_blurred, cv2.CV_64F, 0, 1, ksize=3)  

# grad_x2 = cv2.Sobel(frame2_blurred, cv2.CV_64F, 1, 0, ksize=3)
# grad_y2 = cv2.Sobel(frame2_blurred, cv2.CV_64F, 0, 1, ksize=3)

# # Compute the gradient direction
# angle1 = np.arctan2(grad_y1, grad_x1) * 180 / np.pi  
# angle2 = np.arctan2(grad_y2, grad_x2) * 180 / np.pi

# # Create masks for horizontal edges (within a certain range of angles)
# horizontal_mask1 = (np.abs(angle1) < 10)  
# horizontal_mask2 = (np.abs(angle2) < 10)

# Canny edge detection
edges_frame1 = cv2.Canny(frame1_blurred, threshold1=50, threshold2=150)
edges_frame2 = cv2.Canny(frame2_blurred, threshold1=50, threshold2=150)

# Dilation
kernel = np.ones((5, 5), np.uint8)
dilated_edges1 = cv2.dilate(edges_frame1, kernel, iterations=1)
dilated_edges2 = cv2.dilate(edges_frame2, kernel, iterations=1)

# Closing - clean the edges
closing1 = cv2.morphologyEx(dilated_edges1, cv2.MORPH_CLOSE, kernel)
closing2 = cv2.morphologyEx(dilated_edges2, cv2.MORPH_CLOSE, kernel)

# Plot
plt.figure(figsize=(10, 5))


plt.subplot(2, 2, 1)
plt.imshow(edges_frame1, cmap='gray')
plt.title('Canny Edges Image 1')

plt.subplot(2, 2, 2)
plt.imshow(closing1, cmap='gray')
plt.title('Post-Processed Edges Image 1')

plt.subplot(2, 2, 3)
plt.imshow(edges_frame2, cmap='gray')
plt.title('Canny Edges Image 2')

plt.subplot(2, 2, 4)
plt.imshow(closing2, cmap='gray')
plt.title('Post-Processed Edges Image 2')

plt.show()

print("Edge detection complete.")

cv2.imwrite('edges_frame1.jpg', edges_frame1)
cv2.imwrite('edges_frame2.jpg', edges_frame2)