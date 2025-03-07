import numpy as np
import pandas as pd
from src import config

def preprocess_light_curve(df: pd.DataFrame, time_steps: int = config.TIME_STEPS):
    """
    Preprocess the light curve data:
      - Fills missing values.
      - Normalizes the data.
      - Reshapes the data into (samples, time_steps, 1).
    
    Assumes the DataFrame has a column 'flux' that contains the light curve values.
    """
    # Fill missing values (forward fill as an example)
    data = df['flux'].fillna(method='ffill').values
    
    # Normalize the data
    mean = data.mean()
    std = data.std() if data.std() != 0 else 1  # avoid division by zero
    normalized_data = (data - mean) / std
    
    # Segment the data into chunks of length time_steps
    num_samples = len(normalized_data) // time_steps
    reshaped_data = normalized_data[:num_samples * time_steps].reshape(num_samples, time_steps, 1)
    return reshaped_data

if __name__ == '__main__':
    # Example usage with dummy data
    import pandas as pd
    dummy_df = pd.DataFrame({'flux': [1, 2, 3, 4, 5, 6] * 200})
    processed_data = preprocess_light_curve(dummy_df, time_steps=100)
    print("Processed data shape:", processed_data.shape)
