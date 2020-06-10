import boto3
import json
import zipfile
from io import BytesIO
import io
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')

    try:
      src = s3.Bucket('build.awsome.education')
      dest = s3.Bucket('awsome.education')
      topic = sns.Topic('arn:aws:sns:us-east-1:390758498079:DeployedToProduction')
      
      zip = io.BytesIO()
      src.download_fileobj('build.zip', zip)
      
      with zipfile.ZipFile(zip) as myzip:
        for filename in myzip.namelist():
          fileobj = myzip.open(filename)
          dest.upload_fileobj(fileobj, filename, ExtraArgs={'ContentType': mimetypes.guess_type(filename)[0]})

      print('Job done!')
      topic.publish(Subject='extract-and-deploy SUCCESSFUL', Message='Successful deployment to ' + dest.name)

    except:
      topic.publish(Subject='extract-and-deploy FAILED', Message='Failed deployment to ' + dest.name)
      raise
