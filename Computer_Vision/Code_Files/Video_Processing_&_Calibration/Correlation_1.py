import numpy as np
import matplotlib.pyplot as plt

# Manually enter observed data
angles = np.array([30, 45, 90, 120, 120])  # Degrees
displacements = np.array([15, 22.5, 34.5, 39, 37.8])  # Pixels

# Fit models
# Linear fit: displacement = m * theta + c
linear_coeffs = np.polyfit(angles, displacements, 1)
linear_fit = np.poly1d(linear_coeffs)

# Quadratic fit: displacement = a * theta^2 + b * theta + c
quad_coeffs = np.polyfit(angles, displacements, 2)
quad_fit = np.poly1d(quad_coeffs)

# Sine fit: displacement = A * sin(theta / 2)
# Initial guess and optimization (simplified)
from scipy.optimize import curve_fit
def sine_model(theta, A):
    return A * np.sin(np.radians(theta) / 2)
popt, _ = curve_fit(sine_model, angles, displacements, p0=[50])
sine_A = popt[0]
sine_fit = lambda theta: sine_A * np.sin(np.radians(theta) / 2)

# Generate points for smooth curves
theta_range = np.linspace(0, 150, 200)
linear_values = linear_fit(theta_range)
quad_values = quad_fit(theta_range)
sine_values = sine_fit(theta_range)

# Calculate predicted values for residuals
linear_pred = linear_fit(angles)
quad_pred = quad_fit(angles)
sine_pred = sine_fit(angles)

# Residuals
linear_residuals = displacements - linear_pred
quad_residuals = displacements - quad_pred
sine_residuals = displacements - sine_pred

# RMSE (Root Mean Square Error)
linear_rmse = np.sqrt(np.mean(linear_residuals ** 2))
quad_rmse = np.sqrt(np.mean(quad_residuals ** 2))
sine_rmse = np.sqrt(np.mean(sine_residuals ** 2))

# Plots
plt.figure(figsize=(12, 8))

# Combined plot
plt.subplot(2, 2, 1)
plt.scatter(angles, displacements, color='black', label='Observed Data')
plt.plot(theta_range, linear_values, label='Linear Fit', color='blue')
plt.plot(theta_range, quad_values, label='Quadratic Fit', color='red')
plt.plot(theta_range, sine_values, label='Sine Fit', color='green')
plt.xlabel('Angle (degrees)')
plt.ylabel('Displacement (pixels)')
plt.title('Angle vs. Displacement with Fits')
plt.legend()
plt.grid(True)

# Linear fit plot
plt.subplot(2, 2, 2)
plt.scatter(angles, displacements, color='black', label='Observed Data')
plt.plot(theta_range, linear_values, color='blue', label=f'Linear: y = {linear_coeffs[0]:.2f}x + {linear_coeffs[1]:.2f}')
plt.xlabel('Angle (degrees)')
plt.ylabel('Displacement (pixels)')
plt.title('Linear Fit')
plt.legend()
plt.grid(True)

# Quadratic fit plot
plt.subplot(2, 2, 3)
plt.scatter(angles, displacements, color='black', label='Observed Data')
plt.plot(theta_range, quad_values, color='red', label=f'Quadratic: y = {quad_coeffs[0]:.4f}x^2 + {quad_coeffs[1]:.2f}x + {quad_coeffs[2]:.2f}')
plt.xlabel('Angle (degrees)')
plt.ylabel('Displacement (pixels)')
plt.title('Quadratic Fit')
plt.legend()
plt.grid(True)

# Sine fit plot
plt.subplot(2, 2, 4)
plt.scatter(angles, displacements, color='black', label='Observed Data')
plt.plot(theta_range, sine_values, color='green', label=f'Sine: y = {sine_A:.2f} * sin(θ/2)')
plt.xlabel('Angle (degrees)')
plt.ylabel('Displacement (pixels)')
plt.title('Sine Fit')
plt.legend()
plt.grid(True)

# Display residuals and RMSE
print("Residuals (Observed - Predicted):")
print(f"Linear: {linear_residuals}")
print(f"Quadratic: {quad_residuals}")
print(f"Sine: {sine_residuals}")
print(f"\nRMSE:")
print(f"Linear RMSE: {linear_rmse:.2f} pixels")
print(f"Quadratic RMSE: {quad_rmse:.2f} pixels")
print(f"Sine RMSE: {sine_rmse:.2f} pixels")

plt.tight_layout()
plt.show()