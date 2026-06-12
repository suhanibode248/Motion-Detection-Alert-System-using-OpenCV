# Motion Detection Alert System using OpenCV

## Project Title

Motion Detection Alert System using OpenCV

## Author(s)

Suhani Bode

## Affiliation

Rashtrasant Tukadoji Maharaj Nagpur University, Nagpur

## Date

June 2026

## Abstract

This project presents a real-time motion detection system using Python and OpenCV. The system captures live video through a webcam and detects movement using background subtraction techniques. When motion is detected, it generates alerts, captures snapshots, records videos, and stores event logs. The proposed solution provides an affordable and efficient surveillance system suitable for homes, offices, and educational purposes. Experimental results show that the system performs effectively with low computational requirements and satisfactory accuracy.

## Introduction

Security surveillance is important for protecting people and property. Traditional monitoring systems require continuous human attention, which is inefficient. This project aims to automate surveillance by detecting motion in real time using computer vision techniques. The system reduces human effort and provides immediate responses to suspicious activities.

## Literature Review

Existing motion detection systems use methods such as frame differencing, optical flow, and background subtraction. OpenCV offers efficient implementations of these techniques. Compared to deep learning approaches, classical methods require fewer computational resources and are suitable for low-cost applications.

## Methodology

The webcam continuously captures video frames. Background subtraction (MOG2) is applied to identify moving objects. Noise is reduced using image preprocessing techniques, and contours are analyzed to detect motion. If motion exceeds a threshold, alerts are triggered, snapshots are saved, videos are recorded, and event details are logged.

## Implementation

### Programming Language

* Python

### Frameworks/Libraries

* OpenCV
* NumPy
* CSV Module

### Tools Used

* Visual Studio Code
* Webcam
* GitHub

## Results and Discussion

The system successfully detected motion in real time and generated alerts. Snapshots, video recordings, and logs were created automatically. The system showed reliable performance with minimal processing delay and low hardware requirements.

## Limitation

* Sensitive to lighting changes.
* Cannot identify the type of moving object.
* Detection accuracy depends on camera quality.

## Future Scope

* Face recognition integration.
* Email/SMS notifications.
* Cloud storage support.
* AI-based object classification.
* Remote monitoring through a web dashboard.

## Conclusion

The Motion Detection Alert System provides an effective and low-cost surveillance solution using OpenCV. It automates motion detection and evidence collection, reducing the need for constant monitoring while demonstrating practical applications of computer vision.

## References

[1] Zivkovic, Z., "Improved Adaptive Gaussian Mixture Model for Background Subtraction," 2004.

[2] Bradski, G., "The OpenCV Library," Dr. Dobb's Journal, 2000.

[3] OpenCV Documentation: https://docs.opencv.org/

[4] Python Documentation: https://docs.python.org/
