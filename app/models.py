from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    full_name = Column(String)


class DataSource(Base):
    __tablename__ = "datasource"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    connection_string = Column(String, nullable=False)
    connected = Column(Boolean, default=False)


# class ChatResponseStatus(Enum):
#     success = 'Success'
#     error = 'Error'
#
#
# class ChatResponse(Base):
#     __tablename__ = 'chat_responses'
#     id = Column(Integer, primary_key=True, index=True)
#     message = Column(Text, nullable=False)
#     status = Column(Enum(ChatResponseStatus), nullable=False)
#     additional_info = Column(Text)  # This can be JSON or text, depending on how you want to store it
