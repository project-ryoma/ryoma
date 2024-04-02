import React from "react";
import { Icons } from "@/components/icons";
import { MessageInterface } from "./message-interface";

interface ChatMessageProps {
  message: MessageInterface;
}

// ChatMessage.js
const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const {text, selfFlag, error, image } = message;
  const AvatarIcon = selfFlag ? Icons.user : Icons.aita; // Choose the icon based on who is sending the message

  return (
    <div className="flex items-center justify-start">
      <AvatarIcon className="w-12 h-12 rounded-full text-gray-500" />
      <div className="bg-white shadow p-4 m-2 rounded-lg" id={message.id}>
        {text && <p className={`${error ? 'text-red-500' : 'text-gray-700'}`}>{text}</p>}
        {image && <img src={image} alt="Attached" className="mt-2 rounded" />}
      </div>
    </div>
  );
}

export default ChatMessage;