from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np

app = Flask(__name__)

# Load the trained model; ensure train.py already saved cnn_exoplanet_model.h5 in the root.
try:
    model = load_model("cnn_exoplanet_model.h5")
except Exception as e:
    print("Error loading model:", e)
    model = None

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500

    data = request.get_json().get('data', None)
    if data is None:
        return jsonify({'error': 'No data provided'}), 400

    try:
        # Convert nested lists into a NumPy array and predict
        input_data = np.array(data).astype('float32')
        preds = model.predict(input_data)
        return jsonify({'predictions': preds.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Listen on port 8000
    app.run(host='0.0.0.0', port=8000)