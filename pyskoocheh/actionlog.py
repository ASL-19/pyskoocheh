""" ActionLog Module
    Holds functions for logging file downloads in DynamoDB
"""
import hashlib
import time as systime
import boto3
from botocore.exceptions import ClientError
from errors import AWSError


CLEARED_USER_ID = "-"

# DynamoDB functions
def is_limit_exceeded(user_name, action_name, expiry=85000, table=None):
    """ Access rate limit table in DynamoDB and
        limit to one request per file per 23 hours (85000 seconds)

    Args:
        user_name: address that is requesting this file
        action_name: the email of the file that is being requested
        expiry: seconds until last request expires
    Returns:
        true if limit has been exceeded, false otherwise
    Raises:
        AWSError: when AWS call fails
    """
    dynamodb = boto3.client("dynamodb")
    user_hash = hashlib.sha512(str(user_name)).hexdigest()
    if table is None:
        table = "action_log"

    try:
        requests_today = dynamodb.query(
            TableName=table,
            KeyConditionExpression="user_name = :user_name AND action_time > :action_time",
            FilterExpression="action_name = :action_name",
            ExpressionAttributeValues={
                ":user_name": {"S": str(user_hash)},
                ":action_time": {"N": str(systime.time() - expiry)},
                ":action_name": {"S": str(action_name)},
            })
    except ClientError as error:
        raise AWSError("Unable to retrieve action log: {}".format(str(error)))

    return bool(requests_today["Count"])

def user_has_requested_file(user_name):
    """ Check if user has requested any files before

    Args:
        user_name: unique id of user, username/email/uuid
    Returns:
        true if user has requested a file previously, false otherwise
    Raises:
        AWSError: when AWS call fails
    """
    dynamodb = boto3.client("dynamodb")
    user_hash = hashlib.sha512(str(user_name)).hexdigest()
    try:
        requests = dynamodb.query(
            TableName="action_log",
            KeyConditionExpression="user_name = :user_name",
            Limit=1,
            ExpressionAttributeValues={
                ":user_name": {"S": str(user_hash)}
            })
    except ClientError as error:
        raise AWSError("Unable to retrieve action log: {}".format(str(error)))

    return bool(requests["Count"])

def clear_user_id(age, maxdel = 100):

    """ Clear old records user ids

    Args:
        age: Cleanup records older than age in hours
        maxdel: Maximum number of records to cleanup
    Returns:
        None
    Raises:
        AWSError: dynamodb call failed
    """

    # Convert the age to a proper epoch time
    date_old = systime.time() - age * 3600

    putitem_args = {}
    putitem_args["TableName"] = "action_log"
    putitem_args["FilterExpression"] = "action_time < :date_old"
    putitem_args["ExpressionAttributeValues"] = {
        ":date_old":{"N": str(date_old)}
    }

    dynamodb = boto3.client("dynamodb")
    
    query_done = False
    previous_key = {}
    deleted = 0

    deleted_items = []
    while not query_done:
        if previous_key != {}:
            putitem_args["ExclusiveStartKey"] = previous_key

        try:
            result = dynamodb.scan(**putitem_args)

        except ClientError as error:
            raise AWSError("Unable to query action log: {}".format(str(error)))
        if "LastEvaluatedKey" in result:
            previous_key = result["LastEvaluatedKey"]
        else:
            query_done = True
        # We can use batch_write_item for optimization
        if result["Count"] != 0:
            for item in result["Items"]:

                # We are limiting the number of records to be deleted each time
                deleted += 1
                if deleted > maxdel:
                    break
                    #return maxdel, result["Count"]
                

                try:

                    name = str(item["action_name"]["S"])
                    time = str(item["action_time"]["N"])
                    source = str(item["source"]["S"])
                    log_action(CLEARED_USER_ID, name, source, time, "action_log_cleaned")

                    deleted_items.append({
                            "name": name,
                            "time": time,
                            "source": source
                    })
                    
                    dynamodb.delete_item(
                        TableName = "action_log",
                        Key = {
                            "user_name": item["user_name"],
                            "action_time": item["action_time"]
                        }
                    )

                except ClientError as error:
                    raise AWSError("Unable to update item from action log: {}".format(str(error)))

    return deleted, deleted_items


def clean_action_log(age, maxdel = 100):
    """ Cleanup old records from action log

    Args:
        age: Cleanup records older than age in hours
        maxdel: Maximum number of records to delete
    Returns:
        None
    Raises:
        AWSError: dynamodb call failed
    
    """

    # Convert the age to a proper epoch time
    date_old = systime.time() - age * 3600

    putitem_args = {}
    putitem_args["TableName"] = "action_log"
    putitem_args["FilterExpression"] = "action_time < :date_old"
    putitem_args["ExpressionAttributeValues"] = {
        ":date_old":{"N": str(date_old)}
    }

    dynamodb = boto3.client("dynamodb")

    query_done = False
    previous_key = {}
    deleted = 0

    while not query_done:
        if previous_key != {}:
            putitem_args["ExclusiveStartKey"] = previous_key

        try:
            result = dynamodb.scan(**putitem_args)

        except ClientError as error:
            raise AWSError("Unable to query action log: {}".format(str(error)))

        if "LastEvaluatedKey" in result:
            previous_key = result["LastEvaluatedKey"]
        else:
            query_done = True

        # We can use batch_write_item for optimization
        if result["Count"] != 0:
            for item in result["Items"]:

                # We are limiting the number of records to be deleted each time
                deleted += 1
                if deleted > maxdel:
                    return maxdel, result["Count"]

                try:
                    dynamodb.delete_item(
                        TableName = "action_log",
                        Key = {
                            "user_name": item["user_name"],
                            "action_time": item["action_time"]
                        })

                except ClientError as error:
                    raise AWSError("Unable to delete item from action log: {}".format(str(error)))

    return deleted, result["Count"]

def log_action(user_name, action_name, source, time = None, table = None):
    """ Log action to action_log table for analytics

    Args:
        user_name: unique id of user, username/email/uuid
        action_name: name_of_action
        source: source application name
        time: time if different than the current time
        table: target table name if different than "action_log"
    Returns:
        None
    Raises:
        AWSError: dynamodb call failed
    """
    if time == None:
       time = systime.time()
    if table == None:
       table = "action_log"

    dynamodb = boto3.client("dynamodb")
    user_hash = hashlib.sha512(str(user_name)).hexdigest()
    try:
        dynamodb.put_item(
            TableName=table,
            Item={
                "user_name": {"S": str(user_hash)},
                "action_time": {"N": str(time)},
                "action_name": {"S": str(action_name)},
                "source": {"S": str(source)},
            })
    except ClientError as error:
        raise AWSError("Unable to retrieve action log: {}".format(str(error)))
    return
