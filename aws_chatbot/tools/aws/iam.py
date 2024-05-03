from langchain.tools import tool

from aws_chatbot.lib.aws_session import aws_session
from aws_chatbot.schemas.aws_tool_inputs import (EmptyInput,
                                                 UserPermissionsInput)


@tool(
    args_schema=EmptyInput,
)
def list_all_iam_users() -> dict:
    """
    Retrieves a list of all IAM users in the AWS account. This tool is useful for quickly
    auditing or reviewing all user accounts configured in the AWS IAM service.
    """
    iam = aws_session.client("iam")
    try:
        # Initialize pagination
        paginator = iam.get_paginator("list_users")
        user_list = []

        # Iterate through the pages returned by the API
        for page in paginator.paginate():
            for user in page["Users"]:
                user_list.append(
                    {
                        "UserName": user["UserName"],
                        "UserId": user["UserId"],
                        "CreateDate": user["CreateDate"].strftime("%Y-%m-%d %H:%M:%S"),
                        "Arn": user["Arn"],
                    }
                )

        return {"Users": user_list, "Count": len(user_list)}
    except Exception as e:
        return {"Error": str(e)}


@tool(
    args_schema=UserPermissionsInput,
)
def check_user_permissions(username: str) -> str:
    """
    Retrieves detailed permissions for a specified AWS IAM user by listing and parsing
    the policy documents attached to the user. This tool is intended for comprehensive security audits
    and compliance checks, providing a granular view of what actions the user is authorized to perform.
    """
    iam = aws_session.client("iam")
    try:
        # List attached user policies
        attached_policies = iam.list_attached_user_policies(UserName=username)
        policy_names = [
            policy["PolicyName"]
            for policy in attached_policies.get("AttachedPolicies", [])
        ]

        # List roles that the user is allowed to assume
        role_names = []
        user_policies = iam.list_user_policies(UserName=username)
        for policy_name in user_policies.get("PolicyNames", []):
            policy = iam.get_user_policy(UserName=username, PolicyName=policy_name)
            # Parse policy document for roles (simplified extraction)
            if "assumeRole" in policy["PolicyDocument"]:
                role_names.append(policy["PolicyDocument"]["Statement"]["Resource"])

        if not policy_names and not role_names:
            return f"User {username} has no attached policies or assumable roles."

        response = f"User {username} has attached policies: {', '.join(policy_names)}."
        if role_names:
            response += (
                f" User can assume the following roles: {', '.join(role_names)}."
            )
        else:
            response += "User is not able to assume any roles."

        return response
    except Exception as e:
        return f"Error retrieving information for user {username}: {str(e)}"
