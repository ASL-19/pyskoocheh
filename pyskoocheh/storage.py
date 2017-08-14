""" Storage Module
    Holds functions for working with paskoocheh apps on S3
"""
import json
import re
from datetime import datetime
import requests
import boto3
from boto3.session import Session
from botocore.client import Config
from botocore.exceptions import ClientError
from pyskoocheh.errors import AWSError, ValidationError

S3_AMAZON_LINK = "https://s3.amazonaws.com"

def build_key_name(app_name, os_name, file_name):
    """ Creates key using app name, os and filename

    Args:
        app_name: app name
        os_name: OS the app is written for
        filename: the name of the file
    Returns:
        S3 bucket key for given app/os/filename combination
    """
    return (app_name.replace(" ", "").lower() + "/" +
            os_name.replace(" ", "").lower() + "/" + file_name)

def build_static_link(bucket, key):
    """ Creates a link based on app name os and filename

    Args:
        key: s3 key for the resource
    Returns:
        string url for amazon S3 file
    """
    return "https://s3.amazonaws.com/" + bucket + "/" + key

def get_binary_contents(bucket, key):
    """ Get file contents from S3

    Args:
        bucket: name of bucket
        key: key id in bucket
    Returns:
        Stream object with contents
    Raises:
        AWSError: couldn't fetch file contents from S3
    """
    s3_resource = boto3.resource("s3")
    try:
        response = s3_resource.Object(bucket, key).get()
    except ClientError as error:
        raise AWSError("Error loading file from S3: {}".format(str(error)))
    return response

def put_file_with_creds(bucket, key, content, access_key, secret_key):
    """ Get a file from S3 using Specific Credentials

    Args:
        bucket: name of bucket
        key: key id in bucket
        content: file body content
        access_key: user's access_key
        secret_key: user's secret_key
    Raises:
        AWSError: couldn't fetch file contents from S3
    """ 
    if key is None or len(key) <= 0:
        raise ValidationError("Key name cannot be empty.")

    if bucket is None or len(bucket) <= 0:
        raise ValidationError("Bucket name cannot be empty.")

    s3 = boto3.client("s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key)

    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=content)

    except ClientError as error:
        raise AWSError("Problem putting {} from {} bucket ({})"
                       .format(key, bucket, str(error)))
    return

def get_file_with_creds(bucket, key, access_key, secret_key):
    """ Get a file from S3 using Specific Credentials

    Args:
        bucket: name of bucket
        key: key id in bucket
        access_key: user's access_key
        secret_key: user's secret_key
    Returns:
        Stream object with contents
    Raises:
        AWSError: couldn't fetch file contents from S3
    """ 
    if key is None or len(key) <= 0:
        raise ValidationError("Key name cannot be empty.")

    if bucket is None or len(bucket) <= 0:
        raise ValidationError("Bucket name cannot be empty.")

    s3 = boto3.client("s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key)
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
    except ClientError as error:
        raise AWSError("Error loading file from S3: {}".format(str(error)))
    return response

def get_json_contents(bucket, key):
    """ Get json file from S3

    Args:
        bucket: name of bucket
        key: key id in bucket
    Returns:
        JSON from S3 bucket
    Raises:
        AWSError: couldn't fetch file contents from S3
    """
    s3_resource = boto3.resource("s3")
    try:
        response = s3_resource.Object(bucket, key).get()
    except ClientError as error:
        raise AWSError("Error loading file from S3: {}".format(str(error)))
    return json.load(response["Body"])

def get_object_metadata(bucket, key):
    """ Get file metadata from S3

    Args:
        bucket: name of bucket
        key: key id in bucket
    Returns:
        S3 metadata object
    Raises:
        AWSError: couldn't load metadata from S3
    """
    # Get downloads file metadata from S3 bucket
    s3_resource = boto3.resource("s3")
    obj = s3_resource.Object(bucket, key)
    try:
        obj.load()
    except ClientError as error:
        raise AWSError("Error loading metadata from S3: {}".format(str(error)))
    return obj

def put_object_metadata(bucket, key, meta_key, meta_value):
    """ Get file metadata from S3

    Args:
        bucket: name of bucket
        key: key id in bucket
        meta_key: key for updated metadata
        meta_value: value for updated metadata
    Returns:
        S3 metadata object
    Raises:
        AWSError: couldn't load metadata from S3
    """
    # Get downloads file metadata from S3 bucket
    s3_client = boto3.client("s3")

    try:
        metadata = s3_client.head_object(Bucket=bucket,
                                         Key=key)["Metadata"]
        metadata[meta_key] = meta_value
        s3_client.copy_object(
            Bucket=bucket,
            Key=key,
            CopySource={
                'Bucket': bucket,
                'Key': key,
            },
            Metadata=metadata,
            MetadataDirective='REPLACE'
        )
    except ClientError as error:
        raise AWSError("Error loading metadata from S3: {}".format(str(error)))

def get_temp_link(bucket, key, key_id, secret_key, expiry=300):
    """ Get expiring S3 url with temp token

    NB: bucket must be in us-east-1 to use path addressing!

    Args:
        bucket: name of bucket
        key: key id in bucket
        key_id: Amazon AWS API key id
        secret_key: Amazon AWS Secret API key
        expiry: number of seconds token is valid for (default=600)
    Returns:
        Temporary S3 link to file using temp credentials
    Raises:
        AWSError: error getting presigned link from S3
    """
    # pyskoocheh user credentials
    session = Session(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key
    )
    s3_client = session.client("s3", config=Config(s3={'addressing_style': 'path'}))
    try:
        link = s3_client.generate_presigned_url(
            ExpiresIn=expiry,
            ClientMethod="get_object",
            Params={
                "Bucket": bucket,
                "Key": key,
            }
        )
    except ClientError as error:
        raise AWSError("Error generating temp link: {}".format(str(error)))
    return link

def put_doc_file(bucket, key, filename, url, caption=None, thumb=None):
    """ Appends to a file in S3

    Args:
        bucket: file bucket name
        key: key prefix
        filename: filename to be written
        url: location of filename
        caption: caption file contents
        thumb: thumbnail file contents
    Returns:
        None
    Raises:
        AWSError: Error adding file to S3 bucket
    """
    if key is None or len(key) <= 0:
        raise ValidationError("Key name cannot be empty.")

    s3_resource = boto3.resource("s3")

    timestr = datetime.now().strftime("%Y%m%d-%H:%M:%S.%f-")
    docobj = s3_resource.Object(bucket, key + "/" + timestr + filename)

    if caption is not None:
        capobj = s3_resource.Object(bucket, key + "/" + timestr + filename + ".cap")
    else:
        pass

    if thumb is not None:
        thumbobj = s3_resource.Object(bucket, key + "/" + timestr + filename)

    try:
        file_content = requests.get(url).content
        docobj.put(Body=file_content)
        if caption is not None:
            capobj.put(Body=caption)
        if thumb is not None:
            thumbobj.put(Body=str(thumb))

    except ClientError as error:
        raise AWSError("Problem getting {} from {} bucket ({})"
                       .format(key, bucket, str(error)))
    return

def put_text_file(bucket, key, text):
    """ Appends to a file in S3

    Args:
        bucket: file bucket name
        key: file key name
        text: text to be written
    Returns:
        None
    Raises:
        AWSError: Error adding file to S3 bucket
    """
    if key is None or len(key) <= 0:
        raise ValidationError("Key name cannot be empty.")

    s3_resource = boto3.resource("s3")

    timestr = datetime.now().strftime("%Y%m%d-%H:%M:%S.%f.msg")
    key = key + "/" + timestr
    s3_new_file = s3_resource.Object(bucket, key)

    try:
        s3_new_file.put(Body=text)
    except ClientError as error:
        raise AWSError("Problem getting object {} from {} ({})"
                       .format(key, bucket, str(error)))
    return

def add_to_mailing_list(user_email):
    """ Adds user to mailing list

    Args:
        user_email: unique email of user
    Returns:
        None
    Raises:
        ValidationError: user_email is invalid
    """
    if (user_email is None or len(user_email) <= 0
            or not re.match(r"[^@]+@[^@]+\.[^@]+", user_email)):
        raise ValidationError("User email is invalid: {}".format(user_email))
    return

