import os
import boto3
from botocore.exceptions import ClientError

class LocalStorage:
    def __init__(self, base_path):
        self.base_path = base_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)
    
    def get_file_content(self, file_path):
        """获取文件内容"""
        full_path = os.path.join(self.base_path, file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f'文件不存在: {file_path}')
        
        with open(full_path, 'rb') as f:
            return f.read()
    
    def save_file(self, file_path, content):
        """保存文件"""
        full_path = os.path.join(self.base_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(content)
    
    def delete_file(self, file_path):
        """删除文件"""
        full_path = os.path.join(self.base_path, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)

class S3Storage:
    def __init__(self, access_key, secret_key, bucket, region):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        self.bucket = bucket
    
    def get_file_content(self, file_path):
        """获取文件内容"""
        try:
            response = self.s3.get_object(
                Bucket=self.bucket,
                Key=file_path
            )
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f'文件不存在: {file_path}')
            raise
    
    def save_file(self, file_path, content):
        """保存文件"""
        self.s3.put_object(
            Bucket=self.bucket,
            Key=file_path,
            Body=content
        )
    
    def delete_file(self, file_path):
        """删除文件"""
        try:
            self.s3.delete_object(
                Bucket=self.bucket,
                Key=file_path
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchKey':
                raise 