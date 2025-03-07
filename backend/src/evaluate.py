# filepath: /Users/nickking/Workspace/exoplanet_detection/src/evaluate.py
from tensorflow.keras.models import load_model
import numpy as np

# Load the model
model = load_model("cnn_exoplanet_model.h5")

# Load your test data (X_test and y_test should be prepared beforehand)
# For demonstration, using random data:
X_test = np.random.rand(10, 128, 128, 1).astype('float32')
y_test = np.random.randint(0, 2, size=(10,))

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print("Test Loss:", loss)
print("Test Accuracy:", accuracy)