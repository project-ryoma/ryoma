import React, {useEffect} from 'react';
import ChatMessage from './chat-message';
import hljs from 'highlight.js';
import { MessageInterface } from './message-interface';

function ChatHistory({ messages }: { messages: MessageInterface[] }) {

  useEffect(() => {
    hljs.highlightAll();
  })

  useEffect(() => {
    hljs.highlightAll();
  }, [messages]);
  console.log('messages', messages);

  return (
    <div className="flex-grow overflow-auto">
      {messages.map((message) => (
        <ChatMessage
          key={message.id}
          message={message}
        />
      ))}
    </div>
  );
}

export default ChatHistory;
