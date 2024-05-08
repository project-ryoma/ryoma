import React from "react";
import { Icons } from "@/components/icons";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { MessageInterface } from "./message-interface";
import { useSession } from "next-auth/react";
import { AvatarIcon } from "@radix-ui/react-icons";

interface ChatMessageProps {
  message: MessageInterface;
}

// ChatMessage.js
const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const {text, selfFlag, error, image } = message;
  const { data: session } = useSession();

  return (
    <div className="flex items-center justify-start">
      {(selfFlag) && 
      <Avatar className="h-8 w-8">
        <AvatarImage
          src={session?.user?.image ?? ""}
          alt={session?.user?.name ?? ""}
        />
        <AvatarFallback>{session?.user?.name?.[0]}</AvatarFallback>
      </Avatar>}
      {(!selfFlag) && <Icons.aita className="h-8 w-8" />}
      <div className="bg-white shadow p-4 m-2 rounded-lg" id={message.id}>
        {text && <p className={`${error ? 'text-red-500' : 'text-gray-700'}`}>{text}</p>}
        {image && <img src={image} alt="Attached" className="mt-2 rounded" />}
      </div>
    </div>
  );
}

export default ChatMessage;