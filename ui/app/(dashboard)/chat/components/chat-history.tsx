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

  return (
    <div className="max-h-full overflow-y-auto">
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
