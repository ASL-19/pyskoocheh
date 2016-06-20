""" Conffile Module

    Holds functions for working with conffile Protocol Buffers
"""
import json
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout, TooManyRedirects
from pyskoocheh.errors import AWSError, TelegramError, ValidationError
import protobuf.schemas.python.paskoocheh_pb2 as paskoocheh
import pyskoocheh.storage

def load_config_data(bucket, key):
    """ Load configuration file

    Args:
        bucket: s3 bucket for configuration file
        key: s3 key for configuration file
    Returns:
        File contents
    Raises:
        AWSError: error getting configuration file from s3
        ValidationError: error parsing protocol buffer message
    """
    config_file = paskoocheh.ConfigFile()
    try:
        file_data = storage.get_binary_contents(bucket, key)
    except ClientError as error:
        raise AWSError("Error loading file from S3: {}".format(str(error)))
    config_file.ParseFromString(file_data)
    return conffile

def save_config_data(bucket, key, config_file):
    """ Save configuration file

    Args:
        bucket: s3 bucket to store configuration file in
        key: s3 key to store configuration file at
        conf_file: configuration file object (Protocol Buffer)
    Raises:
        AWSError: error saving configuration file to s3
    """
    file_data = config_file.SerializeToString()
    storage.put_binary_file(bucket, key, file_data)
    return

