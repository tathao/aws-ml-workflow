import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event["s3_key"]
    bucket = event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }


import json
import base64
import boto3

sagemaker_runtime = boto3.client('runtime.sagemaker')

ENDPOINT = "image-classification-2024-11-13-09-54-21-853"

def lambda_handler(event, context):
    image = base64.b64decode(event["body"]["image_data"])
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType='image/png',
        Body=image
        )

    result = response['Body'].read().decode('utf-8')

    event["inferences"] = result
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }


import json

THRESHOLD = .93

def lambda_handler(event, context):
    
    # Grab the inferences from the event
    body = json.loads(event["body"])
    inferences = json.loads(body["inferences"])
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences) > THRESHOLD
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }