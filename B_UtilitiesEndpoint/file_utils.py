import requests
from botocore.exceptions import NoCredentialsError


# Function to generate a presigned URL for an S3 object
def generate_presigned_url(s3_client, bucket_name, object_key, expiration=3600):
    try:
        # Generate the presigned URL
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=expiration,
        )
        return presigned_url
    except NoCredentialsError:
        print("AWS credentials not available")
        return None


def upload_file_to_s3(s3_client, file_path, bucket_name, object_key):
    try:
        with open(file_path, "rb") as data:
            s3_client.upload_fileobj(data, bucket_name, object_key)
        print(f"File uploaded successfully to {object_key}")
    except Exception as e:
        print(f"Error uploading file: {str(e)}")


def download_audio_file(url, object_key):
    response = requests.get(url)
    if response.status_code == 200:
        # Save the file locally
        with open(object_key.split("/")[-1], "wb") as f:
            f.write(response.content)
        print(f"File downloaded and saved as {object_key.split('/')[-1]}")

    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        return None


# Example usage: Get a presigned URL for a specific object in the S3 bucket
# object_key = "path/to/your/object/file.txt"  # Replace with the key of the object you want to generate URL for
# presigned_url = generate_presigned_url(bucket_name, object_key)

# if presigned_url:
#     print(f"Presigned URL for {object_key}: {presigned_url}")
# else:
#     print("Failed to generate presigned URL")
