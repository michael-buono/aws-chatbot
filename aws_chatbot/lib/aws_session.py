import os

import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_session():
    return boto3.session.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
    )


aws_session = create_session()
