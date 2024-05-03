from typing import List

from botocore.exceptions import ClientError
from langchain.tools import tool

from aws_chatbot.lib.aws_session import aws_session
from aws_chatbot.schemas.aws_tool_inputs import (BucketPrefixInput, EmptyInput,
                                                 S3BucketInput, TextData)


@tool(args_schema=EmptyInput)
def check_public_buckets() -> str:
    """
    Scans all S3 buckets in the connected AWS account to determine how many are publicly accessible.
    This tool uses AWS boto3 to list all buckets and check their permissions. It's intended to be used
    when a user needs a security assessment of S3 buckets to ensure private data is not exposed.
    Avoid using this tool for non-security-related inquiries as it specifically checks for public access policies.

    Returns:
    A list of public buckets, or an empty list if there were no public buckets found.
    """
    s3 = aws_session.client("s3")
    bucket_list = s3.list_buckets()

    public_buckets = []
    for bucket in bucket_list["Buckets"]:
        bucket_name = bucket["Name"]
        try:
            # Get public access block configuration
            access_block = s3.get_public_access_block(Bucket=bucket_name)
            settings = access_block["PublicAccessBlockConfiguration"]
            # Check if public access is explicitly blocked; if not, consider public
            if not all(
                [
                    settings["BlockPublicAcls"],
                    settings["IgnorePublicAcls"],
                    settings["BlockPublicPolicy"],
                    settings["RestrictPublicBuckets"],
                ]
            ):
                public_buckets.append(bucket_name)
                continue
        except ClientError as e:
            # If the PublicAccessBlock does not exist, check the bucket policy
            if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                try:
                    # Get bucket policy and check if it allows public access
                    policy = s3.get_bucket_policy(Bucket=bucket_name)
                    if '"Effect": "Allow", "Principal": "*"' in policy["Policy"]:
                        public_buckets.append(bucket_name)
                except ClientError as e:
                    # Handle cases where there is no policy or access is restricted
                    if e.response["Error"]["Code"] != "NoSuchBucketPolicy":
                        print(f"Error getting policy for bucket {bucket_name}: {e}")
        except Exception as e:
            print(f"Error listing buckets: {e}")

    if public_buckets:
        return f"Publicly exposed buckets: {', '.join(public_buckets)}"
        # return public_buckets
    else:
        return "No publicly exposed buckets found."
        # return []


@tool(
    args_schema=BucketPrefixInput,  # Define input schema if necessary
)
def filter_buckets(bucket_prefix: str) -> str:
    """
    Scans all S3 buckets in the connected AWS account and filters for bucket names
    whose name matches a specified bucket_prefix.
    This tool uses AWS boto3 to list all buckets and check for matching prefixes.
    It's intended to be used when a user needs a list of Amazon S3 buckets
    whose names match a prefix.
    Avoid using this tool for non-S3-related inquiries,
    as it specifically checks for bucket prefixes.
    """
    s3 = aws_session.client("s3")
    bucket_list = []
    try:
        # List all buckets
        all_buckets = s3.list_buckets()["Buckets"]

        # Filter buckets based on the prefix
        for bucket in all_buckets:
            if bucket["Name"].startswith(bucket_prefix):
                bucket_list.append(bucket["Name"])
    except Exception as e:
        print(f"Error filtering buckets: {e}")

    return "".join(*bucket_list)


@tool(args_schema=S3BucketInput)
def retrieve_s3_files(bucket_name: str) -> List[str]:
    """
    Retrieves the content of all files in the specified S3 bucket. This tool is intended to
    be used as a preliminary step in workflows requiring analysis of bucket contents, such
    as PII detection or data summarization. Note that often times, this tool will
    not be used to return data to the user directly (for example, if we check whether
    there is sensitive data in the bucket, we do not want to print that to the screen necessarily).
    Instead, think of this tool as an input to other tools, unless the user explicitly asks
    to see the raw bucket contents.

    Note: Do not print the output of this tool to the screen,
    unless you have prompted the user with
    "Are you sure you want to see the raw contents of this bucket?"
    """
    s3_client = aws_session.client("s3")
    contents = []
    try:
        objs = s3_client.list_objects_v2(Bucket=bucket_name)
        for obj in objs.get("Contents", []):
            response = s3_client.get_object(Bucket=bucket_name, Key=obj["Key"])
            contents.append(response["Body"].read().decode("utf-8"))
    except Exception as e:
        print(f"Failed to retrieve files: {e}")
    return contents


@tool(args_schema=TextData)
def detect_pii(text: str) -> str:
    """
    Analyzes the provided text content for personally identifiable information (PII) using
    AWS Comprehend. This tool should be used when sensitive data needs to be identified in
    text, ensuring compliance with data protection regulations, and you should also consult
    this tool when a user asks for a summary or an overview of what data is in a particular
    bucket, as well as generic questions like 'what is in this bucket'.
    This way, we ensure that we alert the user whenever there is sensitive data in a bucket,
    even if the user did not specifically ask for identifying sensitive information.

    Returns: a String representing whether or not there was PII found in the bucket
    """
    comprehend_client = aws_session.client("comprehend")
    try:
        response = comprehend_client.detect_pii_entities(Text=text, LanguageCode="en")
        pii_entities = [
            f"{entity['Type']} (Score: {entity['Score']})"
            for entity in response["Entities"]
        ]
        if pii_entities:
            return (
                f"Detected {len(pii_entities)} PII Entities: {', '.join(pii_entities)}"
            )
        else:
            return "No PII detected."
    except Exception as e:
        print(f"Failed to detect PII: {e}")
        return "Error in PII detection."
