import boto3
import json
import zipfile
from io import StringIO
import io
import mimetypes

def lambda_handler(event, context):
  
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    codepipeline = boto3.client('codepipeline')

    location = {
      'bucketName': 'build.awsome.education',
      'objectKey': 'build.zip'
    }

    topic = sns.Topic('arn:aws:sns:us-east-1:390758498079:DeployedToProduction')
    job = event.get('CodePipeline.job')
    
    try:

      if job:
        for artifact in job['data']['inputArtifacts']:
          if artifact['name'] == 'BuildArtifact':
            location = artifact['location']['s3Location']
      
      print('location: ' + location['bucketName'] + '/' + location['objectKey'])
      
      src = s3.Bucket(location['bucketName'])
      dest = s3.Bucket('awsome.education')

      zip = io.BytesIO()
      src.download_fileobj(location['objectKey'], zip)
      
      with zipfile.ZipFile(zip) as myzip:
        for filename in myzip.namelist():
          fileobj = myzip.open(filename)
          dest.upload_fileobj(fileobj, filename, ExtraArgs={'ContentType': mimetypes.guess_type(filename)[0]})

      topic.publish(Subject='extract-and-deploy SUCCESSFUL', Message='Successful deployment to ' + dest.name)
      response = 'n/a'
      if job:
        response = codepipeline.put_job_success_result(jobId=job['id'])

      print('response: ' + response)

    except Exception as error:
      
      topic.publish(Subject='extract-and-deploy FAILED', Message='Failed deployment') # TODO more info
      response = 'n/a'
      if job:
        response = codepipeline.put_job_failure_result(
          jobId=job['id'],
          failureDetails={
            'type': 'JobFailed',
            'message': f'{error.__class__.__name__}: {str(error)}'
          }
        )

      print('response: ' + str(response))
      raise
