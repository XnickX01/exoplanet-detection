Exoplanet Detection with TESS Data

This repository implements a proof-of-concept machine learning pipeline for exoplanet detection using data from NASA’s TESS mission. The project downloads FITS files from an AWS S3 bucket, processes image data (while skipping non-image table data), and trains a Convolutional Neural Network (CNN) for exoplanet detection. For testing purposes, a simplified script allows you to train the model on a single image.

Overview

The pipeline consists of the following steps:

Data Retrieval: Access FITS files from a public AWS S3 bucket using boto3 with unsigned requests.
Data Loading: Extract image data from FITS files. The loader checks each HDU and only returns data if it contains image information (e.g., primary HDU or extensions with XTENSION="IMAGE").
Preprocessing: Convert and resize image data as needed.
Model Training: Train a CNN on the processed images. A dummy label is used for testing.
Parallel Processing: For efficiency, the loader uses Python’s ThreadPoolExecutor to process multiple FITS files concurrently.
Testing: A separate script (single_image_train.py) is provided to train the model on a single image for quick validation of the pipeline.
Project Structure

exoplanet_detection/
├── data/                   # (Optional) Local data storage
├── notebooks/              # Jupyter notebooks for exploration and visualization
├── src/                    # Source code for the project
│   ├── __init__.py
│   ├── config.py           # Configuration settings (e.g., S3 bucket, hyperparameters)
│   ├── data_loader.py      # Functions to download and process FITS files from S3
│   ├── model.py            # CNN model architecture
│   └── train.py            # Training script for processing multiple files
├── single_image_train.py   # Script to test training on a single image
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation (this file)
Installation

Clone the Repository:
git clone <repository_url>
cd exoplanet_detection
Set Up a Virtual Environment:
It's recommended to use a virtual environment to manage dependencies:

python3 -m venv exoplanet_detection_env
source exoplanet_detection_env/bin/activate
Install Dependencies:
pip install -r requirements.txt
Dependencies include:

boto3
botocore
astropy
numpy
tensorflow (or tensorflow-macos/tensorflow-metal if on Apple Silicon)
scikit-image
(any additional packages your project uses)
Configuration

Update the src/config.py file to set your project-specific variables. For example:

# src/config.py

# AWS S3 Configuration
AWS_S3_BUCKET = "stpubdata"
AWS_S3_PREFIX = "tess/public/ffi/s0001/2018/206/1-1/"

# Model Hyperparameters
EPOCHS = 10
BATCH_SIZE = 32
Usage

Training on Multiple FITS Files
To train the model on FITS files from S3, run:

python3 src/train.py
This script will:

List FITS files in the specified S3 bucket/prefix.
Use multithreading to download and process image data.
Train a CNN model using the processed data.
Save the trained model as cnn_exoplanet_model.h5.
Testing on a Single Image
For quick testing with one image, update the S3 key in single_image_train.py to point to a FITS file that contains image data, then run:

python3 single_image_train.py
This script loads a single FITS image, processes it, trains the model on that one image (with a dummy label), and saves the model.

Troubleshooting

No Valid Data Loaded:
If you see errors such as "No valid data loaded from S3," verify that your S3 bucket and prefix in src/config.py point to FITS files containing image data. Many TESS FITS files may contain table data (XTENSION: BINTABLE) and will be skipped by the loader.
TensorFlow Issues:
Ensure you are using a supported Python version (e.g., Python 3.8 or 3.9) and that TensorFlow is installed correctly for your platform.
Performance:
If the processing seems slow or hangs, consider reducing the number of files processed for testing, lowering the number of threads, or adding more logging to identify bottlenecks.
Future Work

Data Diversity:
Expand the loader to process both image and table FITS files if needed.
Model Improvements:
Experiment with more advanced CNN architectures and hyperparameter tuning.
Deployment:
Develop a REST API for serving the trained model for real-time exoplanet detection.
Continuous Learning:
Implement retraining pipelines as new TESS data becomes available.
License

[Specify your license here, e.g., MIT License]

Acknowledgements

Data from NASA’s TESS mission.
Inspired by research in exoplanet detection and machine learning.


./run_all.sh    