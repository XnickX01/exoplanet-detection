# Exoplanet Detection with TESS Data

This repository implements a proof-of-concept machine learning pipeline for exoplanet detection using data from NASA’s TESS mission. The project downloads FITS files from an AWS S3 bucket, processes image data (while skipping non-image table data), and trains a Convolutional Neural Network (CNN) for exoplanet detection. For testing purposes, a simplified script allows you to train the model on a single image.

## Pipeline Overview

1. **Environment Setup**
   - The project runs a Dockerfile that sets up the environment.
   - A Linux script is then called to install all dependencies and requirements.

2. **Model Training**
   - The training script pulls data from an AWS S3 bucket.
   - FITS files are processed in parallel (currently using a small dataset; the goal is to train on 1,000+ files).

3. **API and Dashboard Integration**
   - The trained model is loaded into a FastAPI Python API.
   - An Angular dashboard is spun up to allow users to interact with the API and predict exoplanet presence in their FITS files.

4. **Docker Image Build**
   - The final Docker image is built for ease of deployment.

## Current Issues

- Downloading FITS files is a lengthy process, even when executed in parallel.

## Future Tasks

- Stream only the important parts of the FITS file instead of downloading it entirely.
- Improve the Angular frontend.
- Add more useful endpoints.
- Train on larger datasets.
- Deploy the solution to AWS.
