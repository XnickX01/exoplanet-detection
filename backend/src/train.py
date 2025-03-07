from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import concurrent
import numpy as np
from skimage.transform import resize  # You may need to install scikit-image: pip install scikit-image
from src import config
from src.data_loader import list_s3_objects, load_fits_image_from_s3
import boto3
import io
from astropy.io import fits
from .memory_monitor import start_memory_monitor
import os


def get_first_valid_hdu_data(file_bytes):
    """
    Iterates through all HDUs in the FITS file and returns the data from the first HDU that is not None.
    """
    try:
        with fits.open(file_bytes) as hdul:
            for idx, hdu in enumerate(hdul):
                if hdu.data is not None:
                    print(f"Using HDU {idx} for data.")
                    return hdu.data
        print("No valid HDU found with data.")
        return None
    except Exception as e:
        print(f"Error reading FITS file: {e}")
        return None


def load_fits_as_table(bucket, key):
    try:
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket, Key=key)
        file_bytes = io.BytesIO(obj['Body'].read())
        with fits.open(file_bytes) as hdul:
            table_data = None
            for idx, hdu in enumerate(hdul):
                if hdu.data is not None:
                    table_data = hdu.data
                    print(f"Using HDU {idx} for table data.")
                    break
        return table_data
    except Exception as e:
        print(f"Error loading table data from {key}: {e}. Please ensure AWS credentials are correctly configured.")
        return None


def table_to_image(table_data, target_shape=(128, 128)):
    """
    Convert table data to a 2D image representation.
    Improved to support structured arrays and handle dimension mismatch.
    """
    try:
        if table_data is not None and len(table_data) > 0:
            # If table_data is structured, try to use a candidate field
            if hasattr(table_data, 'names'):
                candidate_fields = ['SMROW_RAW', 'SMROW_CAL', 'SMROW_ERR',
                                    'VROW_RAW', 'VROW_CAL', 'VROW_ERR']
                for field in candidate_fields:
                    if field in table_data.names:
                        field_data = table_data[field][0]
                        # Clip/pad to match target shape if needed
                        r, c = field_data.shape[:2]
                        r = min(r, target_shape[0])
                        c = min(c, target_shape[1])
                        image_data = field_data[:r, :c]
                        image_data = resize(image_data, target_shape, anti_aliasing=True)
                        return image_data
            # Fallback: convert the first row to a flat array and reshape if possible.
            flat = np.hstack([table_data[name][0].flatten() for name in table_data.names])
            if flat.size >= target_shape[0] * target_shape[1]:
                image_data = flat[:target_shape[0] * target_shape[1]].reshape(target_shape)
                return image_data
        return None
    except Exception as e:
        print(f"Error converting table data to image: {e}")
        return None


def preprocess_fits_image(image_data, target_shape=(128, 128)):
    """
    Convert the FITS image to float32, resize to a fixed shape,
    and add a channel dimension if the image is 2D.
    """
    # Ensure the image data is float32
    image_data = image_data.astype('float32')
    
    # Resize the image to the target shape
    image_data = resize(image_data, target_shape, anti_aliasing=True)
    
    # If the image is 2D, expand dims to add a channel dimension
    if image_data.ndim == 2:
        image_data = image_data[..., np.newaxis]
        
    return image_data


def process_fits_file(key):
    """
    Download and process a single FITS file from S3.
    Now includes extra checks to iterate through HDUs if the initially loaded data is empty.
    """
    try:
        print(f"Processing {key}...")
        image_data = load_fits_image_from_s3(config.AWS_S3_BUCKET, key)

        # If image_data is None or empty, attempt to iterate over HDUs to find valid data.
        if image_data is None or image_data.size == 0:
            print(f"No valid image data in {key}, attempting to retrieve first valid HDU...")
            s3 = boto3.client('s3')
            obj = s3.get_object(Bucket=config.AWS_S3_BUCKET, Key=key)
            file_bytes = io.BytesIO(obj['Body'].read())
            image_data = get_first_valid_hdu_data(file_bytes)

            # If still no valid image data, attempt table conversion.
            if image_data is None or image_data.size == 0:
                print(f"No valid HDU data found in {key}, attempting table conversion...")
                table_data = load_fits_as_table(config.AWS_S3_BUCKET, key)
                if table_data is not None and table_data.size > 0:
                    image_data = table_to_image(table_data, (128, 128))
                else:
                    print(f"No valid table data found in {key}.")
                    return None
        
        # Preprocess image to ensure uniform shape and type.
        image_data = preprocess_fits_image(image_data, target_shape=(128, 128))
        # For demonstration, assign a dummy label (adjust as needed).
        return image_data, 1

    except boto3.exceptions.NoCredentialsError as cred_err:
        print(f"AWS credentials error processing {key}: {cred_err}. Please check your AWS configuration.")
        return None
    except Exception as e:
        print(f"Exception processing {key}: {e}")
        return None
    

def load_and_preprocess_data():
    bucket = config.AWS_S3_BUCKET
    prefix = config.AWS_S3_PREFIX
    objects = list_s3_objects(bucket, prefix)
    
    # Filter for FITS files and limit to a subset for a proof of concept.
    keys = [obj['Key'] for obj in objects if obj['Key'].endswith('.fits')]
    keys = keys[100:120]  # Limit to a subset for proof of concept.
    print(f"Found {len(keys)} FITS files in S3 bucket {bucket} with prefix {prefix}.")

    print("Processing the following FITS files:")
    for key in keys:
        print(key)

    all_data = []
    all_labels = []

    with ProcessPoolExecutor(max_workers=16) as executor:
        future_to_key = {executor.submit(process_fits_file, key): key for key in keys}
        for future in as_completed(future_to_key):
            key = future_to_key[future]
            try:
                # Decrease timeout if needed (e.g., 3 minutes per file)
                result = future.result(timeout=600)
            except concurrent.futures.TimeoutError:
                print(f"Processing of {key} timed out after 3 minutes.")
                continue
            except Exception as e:
                print(f"Exception processing {key}: {e}")
                continue
            if result is None:
                print(f"Skipping {key} since process_fits_file returned None.")
                continue

            data, label = result
            all_data.append(data)
            all_labels.append(label)

    if not all_data:
        raise ValueError("No valid data loaded from S3.")
    return all_data, all_labels


def train_model():
    # Load and preprocess data using parallel processing.
    X, y = load_and_preprocess_data()

    # Convert lists to numpy arrays.
    X = np.array(X)
    y = np.array(y)
    print(f"Loaded {len(X)} samples.")
    print(f"Data shape: {X.shape}, Labels shape: {y.shape}")

    # Build and compile your CNN model using Conv2D.
    from src.model import build_cnn_model
    input_shape = (X.shape[1], X.shape[2], X.shape[3])
    model = build_cnn_model(input_shape=input_shape)
    
    # Train the model (adjust parameters as necessary).
    history = model.fit(X, y, validation_split=0.0, epochs=config.EPOCHS, batch_size=config.BATCH_SIZE)    
    # Save the trained model.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    model_save_path = os.path.join(project_root, "cnn_exoplanet_model.h5")
    model.save(model_save_path)
    print("Model saved as cnn_exoplanet_model.h5")


if __name__ == '__main__':
    start_memory_monitor(threshold_gb=16.0, check_interval=5.0)
    train_model()
