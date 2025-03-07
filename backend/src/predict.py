# filepath: /Users/nickking/Workspace/exoplanet_detection/src/predict.py
from tensorflow.keras.models import load_model
import numpy as np

# Load the saved model
model = load_model("cnn_exoplanet_model.h5")

# Load or preprocess your new data (shape should match the training data)
# For example, let's assume new_data is a NumPy array shaped (samples, 128, 128, 1)
new_data = np.random.rand(1, 128, 128, 1).astype('float32')  # Replace with real data

# Run predictions
predictions = model.predict(new_data)
print("Predictions:", predictions)