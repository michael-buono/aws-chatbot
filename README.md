# AWS Chatbot
A POC of an AWS Chatbot, which uses a LangChain tool-calling agent and custom LangChain tools to answer questions about a user's AWS environment.

## Prerequistes
Here are the steps you must take locally in order to prepare to run the AWS Chatbot.

### OpenAI API key
This project uses the `ChatOpenAI` model from the `langchain_openai` python package, which requires creating an OpenAI account. For more info, head [here](https://platform.openai.com/docs/quickstart).

### Environment Variables
This project uses the `dotenv` python package to set environment variables. As a result, to use this chatbot, you will need to create a `.env` file in the root of this project, and populate it with the appropriate environment variables. Here are the key environment variables you must specify:

* `OPENAI_API_KEY`
* `LANGCHAIN_API_KEY`
* `AWS_ACCESS_KEY_ID`
* `AWS_SECRET_ACCESS_KEY`
* `AWS_DEFAULT_REGION`


For your convenience, `.env.example` is located in the root of the project, so feel free to copy that file to `.env` and fill in the appropriate env variables. Note that as this is a POC, we are using AWS access key and secret key as the means of authentication, but future work would be to leverage STS assume role / more secure ways of authentication. For example, for testing purposes, I created a user in a sandbox AWS account and attached the `ReadOnlyAccess` policy, but this is not advisable for a production account, as this amount of permissions for a user is overly broad and a potential security risk.

If you would like to enable LangSmith tracing, you will need to first create a LangSmith API key (for more information, check out the  [LangSmith docs](https://docs.smith.langchain.com/)). You can then enable tracing by specifying `LANGCHAIN_TRACING_V2="true"` in your `.env` file.


### Running the AWS Chatbot Locally
To start the chatbot, install dependencies via `poetry` and use the `make run` to start the chatbot:

    poetry install
    make run

Here are some example questions you might ask this chatbot:
    
   * _How many S3 buckets do I have?_
   * _Do any of my S3 buckets have PII in them?_
   * _Which S3 buckets that start with "test-" are public?_
   * _What permissions does the user test-user have?_
   * _How many EC2 instances do I have, and what are their sizes?_
