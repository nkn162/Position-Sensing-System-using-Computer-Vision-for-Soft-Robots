import numpy as np
import matplotlib.pyplot as plt

# Manually enter observed data (displacement in pixels, angle in degrees)
displacements = np.array([15, 22.5, 34.5, 39, 37.8])  # Pixels
angles = np.array([30, 45, 90, 120, 120])  # Degrees

# Function to calculate residuals and RMSE
def calculate_residuals_and_rmse(observed, predicted):
    residuals = observed - predicted
    rmse = np.sqrt(np.mean(residuals ** 2))
    return residuals, rmse

# Fit models to predict angle from displacement
# Linear fit: angle = m * displacement + c
linear_coeffs = np.polyfit(displacements, angles, 1)
linear_fit = np.poly1d(linear_coeffs)

# Quadratic fit: angle = a * displacement^2 + b * displacement + c
quad_coeffs = np.polyfit(displacements, angles, 2)
quad_fit = np.poly1d(quad_coeffs)

# Sine fit: angle = 2 * arcsin(displacement / A) * 180 / pi (inverted form)
from scipy.optimize import curve_fit
def sine_model(displacement, A):
    return 2 * np.arcsin(displacement / A) * 180 / np.pi
popt, _ = curve_fit(lambda d, A: 2 * np.arcsin(d / A) * 180 / np.pi, displacements, angles, p0=[50])
sine_A = popt[0]
sine_fit = lambda d: 2 * np.arcsin(d / sine_A) * 180 / np.pi

# Generate points for smooth curves
displacement_range = np.linspace(0, 50, 200)
linear_values = linear_fit(displacement_range)
quad_values = quad_fit(displacement_range)
sine_values = sine_fit(displacement_range)

# Calculate predicted angles for residuals
linear_pred = linear_fit(displacements)
quad_pred = quad_fit(displacements)
sine_pred = sine_fit(displacements)

# Calculate residuals and RMSE for angle
linear_residuals, linear_rmse = calculate_residuals_and_rmse(angles, linear_pred)
quad_residuals, quad_rmse = calculate_residuals_and_rmse(angles, quad_pred)
sine_residuals, sine_rmse = calculate_residuals_and_rmse(angles, sine_pred)

# Plots
plt.figure(figsize=(15, 10))

# Combined plot
plt.subplot(2, 2, 1)
plt.scatter(displacements, angles, color='black', label='Observed Data')
plt.plot(displacement_range, linear_values, label='Linear Fit', color='blue')
plt.plot(displacement_range, quad_values, label='Quadratic Fit', color='red')
plt.plot(displacement_range, sine_values, label='Sine Fit', color='green')
plt.xlabel('Displacement (pixels)')
plt.ylabel('Angle (degrees)')
plt.title('Angle vs. Displacement with Fits')
plt.legend()
plt.grid(True)

# Linear fit plot
plt.subplot(2, 2, 2)
plt.scatter(displacements, angles, color='black', label='Observed Data')
plt.plot(displacement_range, linear_values, color='blue', label=f'Linear: y = {linear_coeffs[0]:.2f}x + {linear_coeffs[1]:.2f}')
plt.xlabel('Displacement (pixels)')
plt.ylabel('Angle (degrees)')
plt.title('Linear Fit')
plt.legend()
plt.grid(True)

# Quadratic fit plot
plt.subplot(2, 2, 3)
plt.scatter(displacements, angles, color='black', label='Observed Data')
plt.plot(displacement_range, quad_values, color='red', label=f'Quadratic: y = {quad_coeffs[0]:.4f}x^2 + {quad_coeffs[1]:.2f}x + {quad_coeffs[2]:.2f}')
plt.xlabel('Displacement (pixels)')
plt.ylabel('Angle (degrees)')
plt.title('Quadratic Fit')
plt.legend()
plt.grid(True)

# Sine fit plot
plt.subplot(2, 2, 4)
plt.scatter(displacements, angles, color='black', label='Observed Data')
plt.plot(displacement_range, sine_values, color='green', label=f'Sine: y = 2 * arcsin(x/{sine_A:.2f}) * 180/π')
plt.xlabel('Displacement (pixels)')
plt.ylabel('Angle (degrees)')
plt.title('Sine Fit')
plt.legend()
plt.grid(True)

# RMSE Bar Plot
plt.figure(figsize=(8, 6))
rmse_values = [linear_rmse, quad_rmse, sine_rmse]
models = ['Linear', 'Quadratic', 'Sine']
plt.bar(models, rmse_values, color=['blue', 'red', 'green'])
plt.xlabel('Model')
plt.ylabel('RMSE (degrees)')
plt.title('RMSE Comparison of Fitting Models')
plt.grid(True)

# Display residuals and RMSE
print("Residuals (Observed Angle - Predicted Angle):")
print(f"Linear: {linear_residuals} degrees")
print(f"Quadratic: {quad_residuals} degrees")
print(f"Sine: {sine_residuals} degrees")
print(f"\nRMSE:")
print(f"Linear RMSE: {linear_rmse:.2f} degrees")
print(f"Quadratic RMSE: {quad_rmse:.2f} degrees")
print(f"Sine RMSE: {sine_rmse:.2f} degrees")

plt.tight_layout()
plt.show()