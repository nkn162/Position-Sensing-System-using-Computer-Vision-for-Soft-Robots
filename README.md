# MRI-Safe Position Sensing for Soft Robotic Actuators via Computer Vision

## Master's Dissertation: A Novel Passive Sensing Approach for MIS

This Master's dissertation addresses a foundational challenge in future medical robotics: **accurate, flexible position sensing for soft actuators operating within the MRI environment.** Traditional sensing methods (EM/FBG sensors) introduce cost, complexity, or compromise the robot's essential compliance.

This project developed and validated a **novel, low-cost, and fully MRI-compatible passive mechanical sensing system** capable of inferring 3D tip position by tracking linear cable displacement using advanced Computer Vision techniques.

| Research Domain | Key Challenges Addressed | Core Technical Solution |
| :--- | :--- | :--- |
| **Computer Vision** | Real-time, sub-millimeter tracking of marked segments across low-contrast video streams. | Custom **Python/OpenCV** pipeline with temporal stability heuristics. |
| **Control & Kinematics** | Actuation control with NEMA 17 steppers; compensating for non-linearities and hysteresis inherent to soft actuators. | Calibrated **Constant Curvature Model (CCM)** firmware (Arduino). |
| **Medical Robotics** | MRI safety, preservation of soft actuator flexibility, low-cost disposal (single-use). | Passive cable displacement mechanism; non-metallic materials. |

---

## Contribution 1: Advanced Computer Vision Pipeline

The project implemented a sophisticated Computer Vision pipeline in **Python (OpenCV)**, optimised for real-time, accurate tracking of cable displacement at the actuator's proximal end.

### 1. Robust Detection & Filtering

The pipeline was engineered to reliably extract displacement data from high-noise, low-feature video frames - static images first before scaling towards video:
* **Pre-processing:** Utilised **CLAHE (Contrast Limited Adaptive Histogram Equalisation)** to locally enhance contrast, successfully resolving cable line visibility where simple global thresholding failed.
* **Feature Extraction:** Employed an adaptive **Canny Edge Detector** followed by a **Probabilistic Hough Transform** to parameterize the fragmented, near-horizontal cable lines.
* **Refinement:** Custom logic applied **Morphological Closing** to fuse broken segments and proximity-based merging to eliminate line duplicates resulting from cable thickness. *(See `Computer_Vision/edge_detection_5.py`)*

### 2. Temporal Tracking & Compensation

The system was scaled for dynamic video analysis, ensuring stability and compensation for physical artifacts during movement:
* **Stability:** **Persistence Logic** was implemented to reuse previous frame coordinates upon transient detection failure, ensuring a continuous and stable data stream at 30 FPS.
* **Motion Modeling:** To smooth inherent latency jumps in the raw coordinates, **Linear Interpolation** was applied to the displacement data between frames, accurately emulating the soft actuator's mechanical movement profile. *(See `Computer_Vision/Sensing_5.py`)*

---

## Contribution 2: Calibrated Kinematic Control Subsystem

To validate the sensing system, a controlled, cable-driven actuation platform was developed using an Arduino Due, integrating a corrected CCM (Constant Curavture Model) to handle the soft robot's mechanical non-linearities.

### 1. Actuator Control Firmware (`Actuator_Control/CCM_Trial_3.ino`)

The firmware implements the core kinematic logic for 3-DoF actuation via serial command (A, J, Z, R) on an **Arduino Due**:
* **Kinematics:** The **CCM** is used to calculate the necessary cable length change ($\Delta L$) for a target bending angle ($\psi$).
* **HMI:** Essential control commands (A: Absolute Move, J: Jog, Z: Zero Position) were implemented to facilitate manual compensation of mechanical slack and hysteresis during experimental resets.

### 2. Experimental Calibration and Correction

Physical trials revealed that the ideal CCM significantly overestimated bending. Analysis corrected the model for compliance, friction, and slack:
* **Correction Parameters:** Empirically derived parameters—**Actuation Efficiency ($\eta = 0.362$ scaling $\Delta L$)** and **Deadband ($\Delta L_0 = 3.04$ mm)**—were introduced and embedded in the firmware's logic to drastically improve prediction accuracy.
* **Hysteresis Analysis:** The experimental procedure included analysing hysteresis (measured up to $8.63^\circ$ at high deflection) and developing operational procedures (the 'Z' command) to mitigate its effect during validation runs.

---

## Contribution 3: Sensing Validation and Research Outcomes

The integrated system validated the viability of CV-based sensing, with quantified accuracy demonstrated through statistical modeling.

### 1. Non-Linear Mapping and Accuracy

* **Model Selection:** **Python regression analysis** was used to model the relationship between pixel displacement and bending angle. The **Quadratic Regression Model** was selected, yielding the lowest total error ($\text{RMSE} = 2.01^\circ$ across the full calibration set) due to its superior fit for the soft robot's intrinsic curvature. *(See `Calibration_Model/Correlation_Performance_2.py`)*
* **Final Accuracy:** The validated sensing system achieved high performance, with errors below **$\text{RMSE} = 0.81^\circ$** for typical surgical deflections ($> 15^\circ$).

### 2. Research Trajectory

This project establishes a strong foundation for advanced research by identifying the precise limitations and the pathway for a next-generation closed-loop control system:
* **Limitation:** Higher error observed at low angles ($\text{RMSE} \approx 3^\circ$), driven by minimal cable displacement visibility.
* **Proposed Solution:** The dissertation concludes that a design shift to **segmented PTFE tubes** would amplify displacement, directly addressing the low-angle sensitivity and paving the way for full-range high-accuracy position sensing. Furthermore, larger calibration data would provide a better fit for the correlation between measured displacement and bending angles. Trials using NDI Aurora Tracker, multi-camera environment, or evaluation against FBG sensors could validate the performance of the proposed sensing system more accurately and provide the pathway to further development of utilsing it for **closed-loop control integration**.

---

## Repository Structure

| Folder | Contents | Key Skills Highlighted |
| :--- | :--- | :--- |
| `Computer_Vision/Code_Files` | `edge_detection_5.py`, `Sensing_5.py` | **Python/OpenCV**, Image Processing (CLAHE, Canny), Temporal Tracking, Signal Processing. |
| `Computer_Vision/Code_Files` | `Correlation_Performance_2.py` | **Non-Linear Regression**, Data Analysis, Statistical Validation (RMSE). |
| `Control/` | `CCM_Trial_3.ino` | **Embedded C (Arduino)**, Stepper Motor Control, **Calibrated Kinematics**, HIL Prototyping. |
| `Output/` | Plots of calibration fit, residual analysis, and prototype schematics. | **Research Visualisation**. |
