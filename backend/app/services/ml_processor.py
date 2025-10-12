# backend/app/services/ml_processor.py
import cv2
import numpy as np

class MLProcessor:
    def __init__(self, model_path=None):
        # Initialize your ML model here
        # self.model = load_your_model(model_path)
        pass

    def process_frame(self, frame):
        """
        Process a single frame with your ML model
        Returns the processed frame
        """
        # Example: Convert to grayscale (replace with your ML model)
        processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)

# Singleton instance
ml_processor = MLProcessor()