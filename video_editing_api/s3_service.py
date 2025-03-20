import boto3
import os
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO

class S3Service:
    def __init__(self, bucket_name: str):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name

    def upload_file(self, file_obj: BinaryIO, s3_key: str, content_type: str) -> bool:
        """
        Upload a file to S3.
        
        Args:
            file_obj: File-like object to upload
            s3_key: The S3 key (path) where the file will be stored
            content_type: The content type of the file
            
        Returns:
            bool: True if upload was successful, False otherwise
        """
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            return True
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return False

    def download_file(self, s3_key: str) -> Optional[bytes]:
        """
        Download a file from S3.
        
        Args:
            s3_key: The S3 key (path) of the file to download
            
        Returns:
            bytes: The file contents if successful, None otherwise
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response['Body'].read()
        except ClientError as e:
            print(f"Error downloading file from S3: {e}")
            return None

    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            s3_key: The S3 key (path) of the file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False

    def get_file_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access to a file.
        
        Args:
            s3_key: The S3 key (path) of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            str: The presigned URL if successful, None otherwise
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None 