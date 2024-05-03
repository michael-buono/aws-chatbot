import uuid
from collections import defaultdict

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langsmith import traceable

from aws_chatbot.tools.aws.ec2 import (get_ec2_instance_summary,
                                       get_ec2_instances)
from aws_chatbot.tools.aws.iam import (check_user_permissions,
                                       list_all_iam_users)
from aws_chatbot.tools.aws.s3 import (check_public_buckets, detect_pii,
                                      filter_buckets, retrieve_s3_files)


class AWSChatbot:
    def __init__(self, verbose=True):
        self._llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        self._tools = [
            check_public_buckets,
            filter_buckets,
            retrieve_s3_files,
            detect_pii,
            check_user_permissions,
            get_ec2_instance_summary,
            get_ec2_instances,
            list_all_iam_users,
        ]

        self._system_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant, with a list of tools that will help you
                    answer questions about a user's AWS account.
                    A few guidelines: do not return raw personally identifiable information to the user.
                    For example, if you find a social security number, do not tell the user what it is.
                    """,
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        self._message_histories = defaultdict(ChatMessageHistory)
        self._tool_calling_agent = create_tool_calling_agent(
            self._llm, self._tools, self._system_prompt
        )
        self._agent_executor = AgentExecutor(
            agent=self._tool_calling_agent, tools=self._tools, verbose=verbose
        )
        self.agent = RunnableWithMessageHistory(
            self._agent_executor,
            lambda session_id: self._message_histories[session_id],
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    @traceable
    def run(self):
        session_id = str(uuid.uuid4())
        print("Welcome to the AWS Management Chatbot. Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Exiting chatbot.")
                break
            response = self.agent.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}},
            )
            print(f"\n\nBot: {response['output']}\n\n")


# Create an instance of the chatbot and run it
if __name__ == "__main__":
    chatbot = AWSChatbot(verbose=False)
    chatbot.run()
