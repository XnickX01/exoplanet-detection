from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tensorflow.keras.models import load_model
import numpy as np

# Optional: Configure CORS if your Angular app is served from a different origin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for your Angular front end (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the request model
class PredictRequest(BaseModel):
    # Expect a list of samples. Each sample should be a 3D array (e.g., 128x128x1)
    data: list

@app.post("/predict")
def predict(request: PredictRequest):
    try:
        # Load your trained model at startup
        model = load_model("cnn_exoplanet_model.h5")
        # Convert incoming list to a NumPy array
        input_data = np.array(request.data, dtype=np.float32)
        # Ensure the input shape matches what your model expects
        predictions = model.predict(input_data)
        return {"predictions": predictions.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the server when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)