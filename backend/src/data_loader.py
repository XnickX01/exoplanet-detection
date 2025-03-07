import boto3
import botocore
import io
from astropy.io import fits
import numpy as np
import concurrent.futures

# Create an S3 client that uses unsigned requests with read and connect timeouts set to 10 seconds
# Python
client_config = botocore.config.Config(
    signature_version=botocore.UNSIGNED,
    read_timeout=180,
    connect_timeout=180
)
s3 = boto3.client('s3', config=client_config)

def list_s3_objects(bucket: str, prefix: str):
    """
    List objects in an S3 bucket under a given prefix.
    """
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return response.get('Contents', [])

def download_file_from_s3(bucket: str, key: str):
    """
    Download a file from S3 and return its contents as bytes.
    """
    response = s3.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()

def load_fits_image_from_s3(bucket: str, key: str):
    """
    Download a FITS file from S3 and extract the image data.
    Returns the first HDU with non-null data.
    If the download takes longer than 3 minutes, skip the file.
    """
    print(f"Downloading {key} from bucket {bucket}...")

    # Use a separate thread to enforce a timeout on the download
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(download_file_from_s3, bucket, key)
            data_bytes = future.result(timeout=180)
    except concurrent.futures.TimeoutError:
        print(f"Download of {key} timed out after 3 minutes.")
        return None
    except Exception as e:
        print(f"Error downloading {key}: {e}")
        return None

    print(f"Downloaded {len(data_bytes)} bytes for {key}")

    with fits.open(io.BytesIO(data_bytes)) as hdul:
        print(f"Opened FITS file with {len(hdul)} HDUs for {key}")
        image_data = None
        for idx, hdu in enumerate(hdul):
            print(f"Processing HDU {idx} for {key}...")
            if hdu.data is not None:
                print(f"HDU {idx} contains data with shape {hdu.data.shape} and dtype {hdu.data.dtype}")
                image_data = hdu.data
                break
            else:
                print(f"HDU {idx} has no data.")
        if image_data is None:
            print(f"No image data found in {key}.")
        else:
            # Handle structured array with named fields
            if image_data.dtype.names is not None:
                try:
                    print(f"Converting structured array from {key} with fields: {image_data.dtype.names}")
                    image_data = np.column_stack(
                        [image_data[name] for name in image_data.dtype.names]
                    ).astype(np.float32)
                    print(f"Structured array converted for {key}, new shape: {image_data.shape}")
                except Exception as e:
                    print(f"Error converting structured array from {key}: {e}")
                    image_data = None
            elif image_data.dtype == 'object':
                try:
                    print(f"Converting object array from {key}")
                    image_data = np.array(image_data, dtype=np.float32)
                    print(f"Object array converted for {key}, new shape: {image_data.shape}")
                except Exception as e:
                    print(f"Error converting object array from {key}: {e}")
                    image_data = None
                    
    return image_data