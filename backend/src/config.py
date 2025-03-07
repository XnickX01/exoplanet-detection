import os

# AWS S3 Configuration
AWS_S3_BUCKET = "stpubdata"
AWS_S3_PREFIX = "tess/"

# Local Data Directory (if needed for caching or local processing)
DATA_LOCAL_PATH = os.path.join(os.getcwd(), "data", "raw")

# Model Hyperparameters
TIME_STEPS = 1000     # Number of time steps in each light curve segment
BATCH_SIZE = 32
EPOCHS = 50
