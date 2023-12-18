from dotenv import load_dotenv
load_dotenv()

import os
import json
import boto3
from botocore.exceptions import ClientError



# Konfigire kle AWS yo
aws_access_key_id = os.getenv("AWS_ACCESS_KEY")
aws_secret_access_key = os.getenv("AWS_SECRET_KEY")

client = boto3.client('s3',           
    aws_access_key_id=aws_access_key_id, 
    aws_secret_access_key=aws_secret_access_key
)

bucket_name = 'l4-survey-final'
object_key = 'results.json'

def read() -> str:
    try:
        response = client.get_object(Bucket=bucket_name, Key=object_key) 
        return response['Body'].read().decode('utf-8')
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', None)
        if error_code == 'NoSuchKey':
            return json.dumps([])
        else:
            print("An Error Occured")
            print(e)

def write(content: str) -> bool:
    try:
        client.put_object(Body=content.encode('utf-8'), Bucket=bucket_name, Key=object_key)
        return True
    except Exception as e:
        print(e)
        return False
    

# client.delete_object(Bucket=bucket_name, Key=object_key)