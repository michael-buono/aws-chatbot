from langchain.pydantic_v1 import BaseModel, Field


class S3BucketInput(BaseModel):
    bucket_name: str = Field(
        description="The name of the S3 bucket to retrieve files from."
    )


class TextData(BaseModel):
    text: str = Field(description="Text content to analyze for PII.")


class EmptyInput(BaseModel):
    pass


class InstanceIPInput(BaseModel):
    ip_address: str = Field(
        description="The public IP address of the EC2 instance to query for its size."
    )


class BucketPrefixInput(BaseModel):
    bucket_prefix: str = Field(
        description="should be a string representing the prefix of an s3 bucket"
    )


class UserPermissionsInput(BaseModel):
    username: str = Field(
        description="The username of the AWS IAM user to check permissions for."
    )
