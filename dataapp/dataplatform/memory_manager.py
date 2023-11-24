from langchain.memory.chat_message_histories import SQLChatMessageHistory
import os


# read configs from environment variables and connection_string to mysql database
MYSQL_HOST = os.environ.get("AZURE_MYSQL_HOST", "localhost")
MYSQL_PORT = os.environ.get("AZURE_MYSQL_PORT", "3306")
MYSQL_USER = os.environ.get("AZURE_MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("AZURE_MYSQL_PASSWORD", "")
MYSQL_MEMORY_DATABASE = os.environ.get("MYSQL_MEMORY_DATABASE", "memory")
SSL_MODE = os.environ.get("SSL_MODE")

# connection_string = "mysql+pymysql://root:@localhost:3306/memory"
connection_string = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_MEMORY_DATABASE}"
print(connection_string)

if SSL_MODE:
    connection_string += f"?ssl={SSL_MODE}"

message_history = SQLChatMessageHistory(
    connection_string=connection_string,
    session_id="aita"
)