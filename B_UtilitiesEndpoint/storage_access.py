import boto3

class S3Client:
    def __init__(self, bucket, key, secret):
        self.bucket = bucket
        self.key = key
        self.secret = secret
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret,
        )

    def get_storage_object(self, object_name) -> str:
        url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": object_name},
            ExpiresIn=300,
        )
        return url
