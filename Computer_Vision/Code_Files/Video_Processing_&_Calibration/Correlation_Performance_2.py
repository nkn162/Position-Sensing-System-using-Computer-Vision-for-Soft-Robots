import numpy as np
import matplotlib.pyplot as plt

# Manually enter observed data (displacement in pixels, angle in degrees)
# Note: Positive displacement for left turn (outside), negative for right turn (inside), but using magnitude for fit
displacements = np.array([15, 16, 15, 16, 15, 22, 22, 23, 22, 23, 34, 34, 33, 34, 34, 39, 39, 38, 38, 39, 41, 41, 41])  # Pixels
angles = np.array([30, 30, 30, 30, 30, 45, 45, 45, 45, 45, 90, 90, 90, 90, 90, 120, 120, 120, 120, 120, 135, 135, 135])  # Degrees
# Data explanation:
# (15, 30): Left turn 30°
# (22.5, 45): Left turn 45°
# (22.5, 45): Right turn 45° (same magnitude, opposite direction)
# (34.5, 90): Left turn 90°
# (39, 120): Left turn 120°
# (37.8, 120): Left turn 120° (second trial)

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
popt, _ = curve_fit(sine_model, displacements, angles, p0=[50])
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
plt.figure(figsize=(15, 12))

# Combined plot
plt.subplot(2, 3, 1)
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
plt.subplot(2, 3, 2)
plt.scatter(displacements, angles, color='black', label='Observed Data')
plt.plot(displacement_range, linear_values, color='blue', label=f'Linear: y = {linear_coeffs[0]:.2f}x + {linear_coeffs[1]:.2f}')
plt.xlabel('Displacement (pixels)')
plt.ylabel('Angle (degrees)')
plt.title('Linear Fit')
plt.legend()
plt.grid(True)

# Quadratic fit plot
plt.subplot(2, 3, 3)
plt.scatter(displacements, angles, color='black', label='Observed Data')
plt.plot(displacement_range, quad_values, color='red', label=f'Quadratic: y = {quad_coeffs[0]:.4f}x^2 + {quad_coeffs[1]:.2f}x + {quad_coeffs[2]:.2f}')
plt.xlabel('Displacement (pixels)')
plt.ylabel('Angle (degrees)')
plt.title('Quadratic Fit')
plt.legend()
plt.grid(True)

# Sine fit plot
plt.subplot(2, 3, 4)
plt.scatter(displacements, angles, color='black', label='Observed Data')
plt.plot(displacement_range, sine_values, color='green', label=f'Sine: y = 2 * arcsin(x/{sine_A:.2f}) * 180/π')
plt.xlabel('Displacement (pixels)')
plt.ylabel('Angle (degrees)')
plt.title('Sine Fit')
plt.legend()
plt.grid(True)

# Residual Plots
# Linear residuals
plt.subplot(2, 3, 5)
x_positions = np.arange(len(displacements))
plt.bar(x_positions - 0.2, linear_residuals, 0.2, color='blue', label='Linear Residuals')
max_linear_res_idx = np.argmax(np.abs(linear_residuals))
plt.bar(max_linear_res_idx - 0.2, linear_residuals[max_linear_res_idx], 0.2, color='yellow', label='Max Residual')
plt.xlabel('Data Point Index')
plt.ylabel('Residual (degrees)')
plt.title('Linear Residuals')
plt.xticks(x_positions, angles, rotation=45)
plt.legend()
plt.grid(True)

# Quadratic residuals
plt.subplot(2, 3, 6)
plt.bar(x_positions + 0.2, quad_residuals, 0.2, color='red', label='Quadratic Residuals')
max_quad_res_idx = np.argmax(np.abs(quad_residuals))
plt.bar(max_quad_res_idx + 0.2, quad_residuals[max_quad_res_idx], 0.2, color='yellow', label='Max Residual')
plt.xlabel('Data Point Index')
plt.ylabel('Residual (degrees)')
plt.title('Quadratic Residuals')
plt.xticks(x_positions, angles, rotation=45)
plt.legend()
plt.grid(True)

plt.subplots_adjust(hspace=0.4)

# Add Sine residuals in a new figure
plt.figure(figsize=(8, 6))
plt.bar(x_positions, sine_residuals, 0.2, color='green', label='Sine Residuals')
max_sine_res_idx = np.argmax(np.abs(sine_residuals))
plt.bar(max_sine_res_idx, sine_residuals[max_sine_res_idx], 0.2, color='yellow', label='Max Residual')
plt.xlabel('Data Point Index')
plt.ylabel('Residual (degrees)')
plt.title('Sine Residuals')
plt.xticks(x_positions, angles)
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