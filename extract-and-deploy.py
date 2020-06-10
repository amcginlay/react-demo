import boto3
import json
import zipfile
from io import BytesIO
import io
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    
    src = s3.Bucket('build.awsome.education')
    dest = s3.Bucket('awsome.education')
    
    zip = io.BytesIO()
    src.download_fileobj('build.zip', zip)
    
    with zipfile.ZipFile(zip) as myzip:
      for filename in myzip.namelist():
        fileobj = myzip.open(filename)
        dest.upload_fileobj(fileobj, filename, ExtraArgs={'ContentType': mimetypes.guess_type(filename)[0]})
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
