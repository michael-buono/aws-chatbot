from dotenv import load_dotenv

from aws_chatbot.chatbot import AWSChatbot

load_dotenv()


if __name__ == "__main__":
    chatbot = AWSChatbot()
    chatbot.run()
