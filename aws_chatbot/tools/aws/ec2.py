from langchain.tools import tool

from aws_chatbot.lib.aws_session import aws_session
from aws_chatbot.schemas.aws_tool_inputs import EmptyInput, InstanceIPInput


def instance_summary(instance):
    return {
        "Name": next(
            (tag["Value"] for tag in instance.tags if tag["Key"] == "Name"),
            "Unnamed Instance",
        ),
        "Instance Type": instance.instance_type,
        "State": instance.state["Name"],
        "Public IP": instance.public_ip_address,
        "Private IP": instance.private_ip_address,
        "Launch Time": instance.launch_time.strftime("%Y-%m-%d %H:%M:%S"),
        "AMI ID": instance.image_id,
        "VPC ID": instance.vpc_id,
        "Subnet ID": instance.subnet_id,
        "Security Groups": [sg["GroupName"] for sg in instance.security_groups],
    }


@tool(
    args_schema=EmptyInput,
)
def get_ec2_instances() -> dict:
    """
    Retrieves a summary of all Amazon EC2 instances. This summary includes
    detailed attributes like the instance type, state, and other relevant details in a structured dictionary.
    This tool is useful for comprehensive insights into the characteristics and status of all EC2 instances,
    or for getting a list of running ec2 instances in order to answer questions about one in particular.
    """
    ec2 = aws_session.resource("ec2")

    running_instances = ec2.instances.filter()

    return [instance_summary(instance) for instance in running_instances]


@tool(
    args_schema=InstanceIPInput,
)
def get_ec2_instance_summary(ip_address: str) -> dict:
    """
    Retrieves a summary of an Amazon EC2 instance based on its IP address. This summary includes
    detailed attributes like the instance type, state, and other relevant details in a structured dictionary.
    This tool is useful for comprehensive insights into the characteristics and status of an EC2 instance.
    """
    ec2 = aws_session.resource("ec2")
    filters = [{"Name": "ip-address", "Values": [ip_address]}]

    running_instances = ec2.instances.filter(Filters=filters)
    return [instance_summary(instance) for instance in running_instances]
