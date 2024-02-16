"use client";
import ChatForm from "@/components/forms/chat-form"
import ChatHistory from "@/components/chat/chat-history";
import { MessageInterface } from "./message-interface";
import { useState } from "react";
import * as z from "zod";
import axios from "axios";

const formSchema = z.object({
  question: z.string(),
});

function ChatBoard() {
  const [messages, setMessages] = useState<MessageInterface[]>([]);
  const [prompt, setPrompt] = useState<string>('');
  const [promptToRetry, setPromptToRetry] = useState<string | null>(null);
  const [uniqueIdToRetry, setUniqueIdToRetry] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  let loadInterval: number | undefined;


  const generateUniqueId = () => {
    const timestamp = Date.now();
    const randomNumber = Math.random();
    const hexadecimalString = randomNumber.toString(16);

    return `id-${timestamp}-${hexadecimalString}`;
  }

  const htmlToText = (html: string) => {
    const temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.textContent;
  }

  const delay = (ms: number) => {
    return new Promise( resolve => setTimeout(resolve, ms) );
  }

  const addLoader = (uid: string) => {
    const element = document.getElementById(uid) as HTMLElement;

    element.textContent = ''

    // @ts-ignore
    loadInterval = setInterval(() => {
      // Update the text content of the loading indicator
      element.textContent += '.';

      // If the loading indicator has reached three dots, reset it
      if (element.textContent === '....') {
        element.textContent = '';
      }
    }, 300);
  }

  const addMessage = (selfFlag: boolean, message?: string) => {
    const uid = generateUniqueId()
    setMessages(prevMessages => [
      ...prevMessages,
      {
        id: uid,
        text: message,
        selfFlag,
      },
    ]);
    return uid;
  }

  const updateMessage = (uid: string, updatedObject: Record<string, unknown>) => {
    setMessages(prevMessages => {
      const updatedMessages = [...prevMessages]
      const index = prevMessages.findIndex((message) => message.id === uid);
      if (index > -1) {
        updatedMessages[index] = {
          ...updatedMessages[index],
          ...updatedObject,
        }
      }
      return updatedMessages;
    });
  }

  const onSubmit = async (values: z.infer<typeof formSchema>, _uniqueIdToRetry?: string | null) =>{
    const { question } = values;

    // Get the prompt input
    const _prompt = question ?? htmlToText(prompt);

    // If a response is already being generated or the prompt is empty, return
    if (loading || !_prompt) {
      return;
    }

    setLoading(true);

    // Clear the prompt input
    setPrompt('');

    let uniqueId: string;
    if (_uniqueIdToRetry) {
      uniqueId = _uniqueIdToRetry;
    } else {
      // Add the self prompt to the response list
      addMessage(true, _prompt);
      uniqueId = addMessage(false);
      await delay(50);
      addLoader(uniqueId);
    }

    try {
      // Send a POST request to the API with the prompt in the request body
      const response = await axios.post('/api/py/chat', {
        prompt: _prompt,
      });

      updateMessage(uniqueId, {
        text: response.data.message.trim(),
      });

      setPromptToRetry(null);
      setUniqueIdToRetry(null);

    } catch (err) {
      setPromptToRetry(_prompt);
      setUniqueIdToRetry(uniqueId);
      updateMessage(uniqueId, {
        // @ts-ignore
        text: `Error: ${err.message}`,
        error: true
      });
    } finally {
      // Clear the loader interval
      clearInterval(loadInterval);
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <ChatHistory messages={messages} />
      <div className="p-4 bg-white border-t border-gray-200">
        <ChatForm onSubmit={onSubmit} loading={loading}  />
      </div>
    </div>
  );
}

export default ChatBoard;